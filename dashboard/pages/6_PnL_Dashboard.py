"""Airline P&L Dashboard — portfolio-level summary across saved scenarios."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · P&L Dashboard", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section, kpi_row, apply_theme, empty_state
from dashboard._shared.styles import COLORS
from dashboard.utils.auth import require_auth, show_user_menu
inject_css()
require_auth()

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd, numpy as np
from economics.scenario_store import list_scenarios, compare_scenarios
from dashboard.utils.exporter import export_excel, export_pdf

with st.sidebar:
    sidebar_logo()
    show_user_menu()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>',
                unsafe_allow_html=True)

page_header(
    "Executive Intelligence", "Airline P&L Dashboard",
    "Portfolio-level profitability across all your saved route scenarios."
)
C = COLORS

# ── Load saved scenarios ──────────────────────────────────────────────────────
saved = list_scenarios()

if not saved:
    empty_state(
        "📊",
        "No saved scenarios yet",
        "Build and save routes in the Route Builder first. "
        "Each saved scenario appears here as part of your network P&L.",
        "→ Go to Route Builder to create scenarios"
    )
    st.stop()

scenarios = compare_scenarios(saved)

# ── Build portfolio dataframe ─────────────────────────────────────────────────
rows = []
for sc in scenarios:
    e = sc["economics"]
    rows.append({
        "scenario":       sc["name"],
        "route":          f"{e['origin']} → {e['destination']}",
        "origin":         e["origin"],
        "destination":    e["destination"],
        "airline":        e["airline_code"],
        "aircraft":       e["aircraft_type"],
        "distance_km":    e["distance_km"],
        "load_factor":    e["load_factor"],
        "daily_freq":     e["daily_frequency"],
        "rask":           e["rask"],
        "cask":           e["cask"],
        "margin_pct":     e["margin_pct"],
        "belf":           e["belf"],
        "lf_cushion":     e["lf_cushion"],
        "revenue":        e["total_revenue_inr"],
        "fuel_cost":      e["fuel_cost_inr"],
        "crew_cost":      e["crew_cost_inr"],
        "maintenance":    e["maintenance_cost_inr"],
        "airport_cost":   e["airport_cost_inr"],
        "overhead":       e["overhead_cost_inr"],
        "total_cost":     e["total_cost_inr"],
        "profit":         e["profit_inr"],
        "ask":            e["ask"],
        "rpk":            e["rpk"],
    })

df = pd.DataFrame(rows)
n = len(df)
profitable = (df["margin_pct"] > 0).sum()
loss_making = (df["margin_pct"] < 0).sum()
total_revenue = df["revenue"].sum()
total_cost    = df["total_cost"].sum()
total_profit  = df["profit"].sum()
avg_margin    = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
avg_rask      = df["rask"].mean()
avg_cask      = df["cask"].mean()
avg_belf      = df["belf"].mean()
total_ask     = df["ask"].sum()
total_rpk     = df["rpk"].sum()
network_lf    = total_rpk / total_ask if total_ask > 0 else 0

# ── Network KPIs ──────────────────────────────────────────────────────────────
section("Network P&L Summary  ·  Daily")
kpi_row([
    {"label": "Total Routes",      "value": str(n), "variant": "accent"},
    {"label": "Profitable",        "value": f"{profitable}/{n}",
     "variant": "positive" if profitable/n >= 0.6 else "negative"},
    {"label": "Network Margin",    "value": f"{avg_margin:.1f}%",
     "variant": "positive" if avg_margin > 0 else "negative",
     "delta": f"₹{abs(total_profit)/1e5:.1f}L daily {'profit' if total_profit >= 0 else 'loss'}",
     "delta_pos": total_profit >= 0},
    {"label": "Network RASK",      "value": f"{avg_rask:.1f}p"},
    {"label": "Network CASK",      "value": f"{avg_cask:.1f}p",
     "variant": "negative" if avg_cask > avg_rask else ""},
])

r1, r2, r3, r4 = st.columns(4)
r1.metric("Total Daily Revenue", f"₹{total_revenue/1e5:.1f}L")
r2.metric("Total Daily Cost",    f"₹{total_cost/1e5:.1f}L")
r3.metric("Network BELF",        f"{avg_belf*100:.1f}%")
r4.metric("Network Load Factor", f"{network_lf:.1%}")

# ── P&L Waterfall ─────────────────────────────────────────────────────────────
section("Daily Revenue → Cost → Profit Waterfall")
cost_breakdown = {
    "Total Revenue": total_revenue,
    "Fuel":          -df["fuel_cost"].sum(),
    "Crew":          -df["crew_cost"].sum(),
    "Maintenance":   -df["maintenance"].sum(),
    "Airport":       -df["airport_cost"].sum(),
    "Overhead":      -df["overhead"].sum(),
    "Net Profit":    total_profit,
}
values = list(cost_breakdown.values())
labels = list(cost_breakdown.keys())
colors_wf = [C["green"]] + [C["red"]]*5 + \
            ([C["green"]] if total_profit >= 0 else [C["red"]])

fig = go.Figure(go.Waterfall(
    name="Daily P&L",
    orientation="v",
    measure=["absolute"] + ["relative"]*5 + ["total"],
    x=labels,
    y=[v/1e5 for v in values],
    text=[f"₹{abs(v)/1e5:.1f}L" for v in values],
    textposition="outside",
    textfont=dict(size=10, color=C["text3"]),
    increasing=dict(marker_color=C["green"]),
    decreasing=dict(marker_color=C["red"]),
    totals=dict(marker_color=C["green"] if total_profit >= 0 else C["red"]),
    connector=dict(line=dict(color=C["border"], width=1, dash="dot")),
))
apply_theme(fig, "Network P&L Waterfall  (₹ Lakhs/day)", 380)
fig.update_layout(yaxis_title="₹ Lakhs", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ── Route-level P&L bars ──────────────────────────────────────────────────────
section("Route-Level Profitability")
df_sorted = df.sort_values("profit", ascending=True)

fig2 = go.Figure(go.Bar(
    x=df_sorted["profit"] / 1e5,
    y=df_sorted["route"],
    orientation="h",
    marker_color=[C["green"] if p >= 0 else C["red"]
                  for p in df_sorted["profit"]],
    marker_line_width=0,
    text=[f"₹{p/1e5:.1f}L  ({m:.1f}%)"
          for p, m in zip(df_sorted["profit"], df_sorted["margin_pct"])],
    textposition="outside",
    textfont=dict(size=9, color=C["text3"]),
    hovertemplate="%{y}<br>Profit: ₹%{x:.2f}L/day<extra></extra>",
))
fig2.add_vline(x=0, line_color=C["border"], line_width=1.5)
apply_theme(fig2, "Daily Profit per Route  (₹ Lakhs)", max(320, n * 40))
fig2.update_layout(xaxis_title="Daily Profit (₹ Lakhs)", yaxis_title="",
                    showlegend=False,
                    margin=dict(l=140, r=60, t=40, b=14))
st.plotly_chart(fig2, use_container_width=True)

# ── RASK vs CASK scatter ──────────────────────────────────────────────────────
section("RASK vs CASK  ·  Network Overview")
fig3 = go.Figure()

for _, row in df.iterrows():
    color = C["green"] if row["margin_pct"] > 2 else \
            C["red"] if row["margin_pct"] < 0 else C["amber"]
    fig3.add_trace(go.Scatter(
        x=[row["cask"]], y=[row["rask"]],
        mode="markers+text",
        marker=dict(size=max(10, min(20, abs(row["profit"])/1e5*2)),
                    color=color, opacity=0.8,
                    line=dict(color=C["border"], width=1)),
        text=[row["route"]],
        textposition="top center",
        textfont=dict(size=9, color=C["text2"]),
        name=row["route"],
        showlegend=False,
        hovertemplate=f"{row['route']}<br>RASK: {row['rask']:.1f}p | CASK: {row['cask']:.1f}p<br>Margin: {row['margin_pct']:.1f}%<extra></extra>",
    ))

all_vals = df["cask"].tolist() + df["rask"].tolist()
lo_v, hi_v = min(all_vals)*0.88, max(all_vals)*1.12
fig3.add_trace(go.Scatter(
    x=[lo_v, hi_v], y=[lo_v, hi_v], mode="lines",
    line=dict(color=C["amber"], dash="dash", width=1.5),
    name="Break-Even Line",
))
apply_theme(fig3, "RASK vs CASK Scatter  ·  Bubble size = daily profit  ·  Above diagonal = profitable", 420)
fig3.update_layout(xaxis_title="CASK (p/ASK)", yaxis_title="RASK (p/ASK)")
st.plotly_chart(fig3, use_container_width=True)

# ── Cost composition ──────────────────────────────────────────────────────────
section("Network Cost Composition")
cost_cols = ["fuel_cost", "crew_cost", "maintenance", "airport_cost", "overhead"]
cost_labels = ["Fuel", "Crew", "Maintenance", "Airport", "Overhead"]
cost_totals = [df[c].sum()/1e5 for c in cost_cols]
cost_pcts = [c/sum(cost_totals)*100 for c in cost_totals]

cc1, cc2 = st.columns(2)
with cc1:
    fig4 = go.Figure(go.Pie(
        labels=cost_labels,
        values=cost_totals,
        hole=0.55,
        marker_colors=[C["accent"], C["green"], C["amber"], C["red"], C["text3"]],
        textinfo="label+percent",
        textfont=dict(size=11, color=C["text"]),
        hovertemplate="%{label}<br>₹%{value:.1f}L/day (%{percent})<extra></extra>",
    ))
    fig4.add_annotation(text=f"₹{sum(cost_totals):.1f}L<br>total/day",
                         font=dict(size=12, color=C["text2"]), showarrow=False)
    apply_theme(fig4, "Network Cost Breakdown", 340)
    fig4.update_layout(showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

with cc2:
    # Fuel cost as % of total cost per route
    df["fuel_pct"] = df["fuel_cost"] / df["total_cost"] * 100
    df_fp = df.sort_values("fuel_pct", ascending=True)
    fig5 = go.Figure(go.Bar(
        x=df_fp["fuel_pct"], y=df_fp["route"],
        orientation="h",
        marker_color=C["amber"], marker_line_width=0,
        text=[f"{p:.0f}%" for p in df_fp["fuel_pct"]],
        textposition="outside",
        textfont=dict(size=9, color=C["text3"]),
    ))
    apply_theme(fig5, "Fuel Cost as % of Total Cost per Route", 340)
    fig5.update_layout(xaxis_title="Fuel %", yaxis_title="",
                        showlegend=False,
                        margin=dict(l=120, r=40, t=40, b=14))
    st.plotly_chart(fig5, use_container_width=True)

# ── Full portfolio table ───────────────────────────────────────────────────────
section("Full Portfolio Table")
disp = df[[
    "route", "airline", "aircraft", "load_factor",
    "rask", "cask", "margin_pct", "belf", "revenue", "total_cost", "profit"
]].copy()
disp.columns = [
    "Route", "Airline", "Aircraft", "LF",
    "RASK (p)", "CASK (p)", "Margin %", "BELF",
    "Daily Rev", "Daily Cost", "Daily Profit"
]
disp["LF"]          = disp["LF"].map("{:.1%}".format)
disp["BELF"]        = disp["BELF"].map("{:.1%}".format)
disp["Daily Rev"]   = disp["Daily Rev"].map("₹{:,.0f}".format)
disp["Daily Cost"]  = disp["Daily Cost"].map("₹{:,.0f}".format)
disp["Daily Profit"]= disp["Daily Profit"].map("₹{:,.0f}".format)
st.dataframe(disp, use_container_width=True, hide_index=True)

# ── Export ─────────────────────────────────────────────────────────────────────
section("Export")
ex1, ex2 = st.columns(2)
with ex1:
    excel_bytes = export_excel(
        type('obj', (object,), {
            'origin': 'Network', 'destination': 'Portfolio',
            'airline_code': 'ALL', 'aircraft_type': 'Mixed',
            'distance_km': 0, 'seats': 0, 'load_factor': network_lf,
            'daily_frequency': int(df['daily_freq'].sum()),
            'rask': avg_rask, 'cask': avg_cask,
            'total_revenue_inr': total_revenue, 'fuel_cost_inr': df['fuel_cost'].sum(),
            'crew_cost_inr': df['crew_cost'].sum(), 'maintenance_cost_inr': df['maintenance'].sum(),
            'airport_cost_inr': df['airport_cost'].sum(), 'overhead_cost_inr': df['overhead'].sum(),
            'total_cost_inr': total_cost, 'profit_inr': total_profit,
            'margin_pct': avg_margin, 'belf': avg_belf,
            'lf_cushion': network_lf - avg_belf,
            'ask': total_ask, 'rpk': total_rpk, 'flight_time_hr': 0,
        })(), scenarios
    )
    st.download_button("↓ Export Excel", excel_bytes,
                        "aerovia_pnl_dashboard.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
with ex2:
    st.download_button("↓ Export Portfolio CSV", df.to_csv(index=False),
                        "aerovia_portfolio_pnl.csv", "text/csv",
                        use_container_width=True)
