"""Route Builder — Streamlit page."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · Route Builder", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section, kpi_row, route_meta_bar, apply_theme
from dashboard._shared.styles import COLORS
inject_css()

import plotly.graph_objects as go
from config.constants import (INDIAN_AIRPORTS, AIRLINES, AIRCRAFT_TYPES,
                               DEFAULT_COST_ASSUMPTIONS, AIRLINE_DESTINATIONS,
                               AIRLINE_AIRCRAFT, get_airline_airports)
from economics.engine import RouteInputs, compute_route_economics
from economics.scenario_store import save_scenario

with st.sidebar:
    sidebar_logo()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>', unsafe_allow_html=True)

page_header("Route Economics", "Route Builder",
            "Select an airline — destinations update automatically to reflect its actual network.")

C = COLORS

# ── Step 1: Airline first ─────────────────────────────────────────────────────
section("Select Airline")
al_cols = st.columns(len(AIRLINES))
airline = None
for i, (code, info) in enumerate(AIRLINES.items()):
    with al_cols[i]:
        selected = st.session_state.get("selected_airline") == code
        btn_style = f"background:{info['color']};color:#fff;border:none;" if selected else ""
        if st.button(
            f"{info['name']}\n{info['type']}",
            key=f"al_{code}",
            use_container_width=True,
            help=f"{info['name']} · {info['type']}"
        ):
            st.session_state["selected_airline"] = code
            st.rerun()

if "selected_airline" not in st.session_state:
    st.session_state["selected_airline"] = "6E"

airline = st.session_state["selected_airline"]
al_info = AIRLINES[airline]

# Show selected airline badge
st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;margin:8px 0 4px">
  <div style="background:{al_info['color']};color:#fff;padding:5px 14px;
              border-radius:20px;font-size:12px;font-weight:700;letter-spacing:0.3px">
    {al_info['name']} · {al_info['type']}
  </div>
  <span style="font-size:12px;color:var(--text-3)">
    {len(AIRLINE_DESTINATIONS.get(airline,{}).get('domestic',[]))} domestic destinations
  </span>
</div>
""", unsafe_allow_html=True)

# ── Step 2: Route (filtered by airline) ───────────────────────────────────────
section("Route Configuration")

airline_aps = get_airline_airports(airline)
if not airline_aps:
    st.warning("No destination data for this airline.")
    st.stop()

ap_options = {f"{k} — {v['city']}": k for k, v in sorted(airline_aps.items(), key=lambda x: x[1]['city'])}

c1, c2, c3 = st.columns(3)
with c1:
    origin_label = st.selectbox("Origin Airport", list(ap_options.keys()), index=0,
                                  help=f"All {len(ap_options)} {al_info['name']} domestic destinations")
    origin = ap_options[origin_label]
with c2:
    dest_options = {k: v for k, v in ap_options.items() if v != origin}
    # Default to a different city
    dest_list = list(dest_options.keys())
    default_dest_idx = min(5, len(dest_list)-1)
    dest_label = st.selectbox("Destination Airport", dest_list, index=default_dest_idx)
    destination = dest_options[dest_label]
with c3:
    default_ac = AIRLINE_AIRCRAFT.get(airline, "A320")
    ac_idx = list(AIRCRAFT_TYPES.keys()).index(default_ac) if default_ac in AIRCRAFT_TYPES else 0
    aircraft_type = st.selectbox("Aircraft Type", list(AIRCRAFT_TYPES.keys()), index=ac_idx)
    ac = AIRCRAFT_TYPES[aircraft_type]
    st.caption(f"{ac['seats']} seats · {ac['speed_kmh']} km/h · {ac['fuel_burn_kg_hr']} kg/hr")

c4, c5 = st.columns(2)
with c4:
    daily_freq = st.number_input("Daily Frequency", min_value=1, max_value=12, value=3)
with c5:
    load_factor = st.slider("Load Factor", 40, 100, 82, format="%d%%") / 100

# ── Step 3: Cost Assumptions ───────────────────────────────────────────────────
section("Cost Assumptions")
with st.expander("Customize cost inputs  —  defaults are 2024 Indian aviation benchmarks", expanded=False):
    e1, e2, e3 = st.columns(3)
    with e1:
        atf = st.number_input("ATF Price (₹/litre)", value=DEFAULT_COST_ASSUMPTIONS["atf_price_inr_per_litre"], step=1.0, format="%.1f")
        crew_pct = st.number_input("Crew Cost (% of revenue)", value=DEFAULT_COST_ASSUMPTIONS["crew_cost_pct_of_revenue"]*100, step=0.5, format="%.1f") / 100
    with e2:
        maint = st.number_input("Maintenance (₹/flight hr)", value=float(DEFAULT_COST_ASSUMPTIONS["maintenance_cost_per_flight_hour"]), step=500.0)
        airport_ch = st.number_input("Airport Charges (₹/sector)", value=float(DEFAULT_COST_ASSUMPTIONS["airport_charges_per_sector"]), step=500.0)
    with e3:
        overhead_pct = st.number_input("Overhead (% of revenue)", value=DEFAULT_COST_ASSUMPTIONS["overhead_pct_of_revenue"]*100, step=0.5, format="%.1f") / 100
        yield_inr = st.number_input("Yield (₹/RPK)", value=DEFAULT_COST_ASSUMPTIONS["avg_yield_inr_per_km"], step=0.1, format="%.2f")

inputs = RouteInputs(
    origin=origin, destination=destination, airline_code=airline,
    aircraft_type=aircraft_type, daily_frequency=daily_freq, load_factor=load_factor,
    atf_price_inr_per_litre=atf, crew_cost_pct=crew_pct,
    maintenance_cost_per_fh=maint, airport_charges_per_sector=airport_ch,
    overhead_pct=overhead_pct, yield_inr_per_km=yield_inr,
)
econ = compute_route_economics(inputs)

route_meta_bar(origin, destination, econ.distance_km, econ.flight_time_hr, econ.margin_pct)

# ── KPIs ───────────────────────────────────────────────────────────────────────
section("Key Performance Indicators")
kpi_row([
    {"label": "RASK",          "value": f"{econ.rask:.1f}p",   "sub": "Revenue per ASK", "variant": "accent"},
    {"label": "CASK",          "value": f"{econ.cask:.1f}p",   "sub": "Cost per ASK",
     "variant": "negative" if econ.cask > econ.rask else ""},
    {"label": "Net Margin",    "value": f"{econ.margin_pct:.1f}%",
     "variant": "positive" if econ.margin_pct > 0 else "negative",
     "delta": f"₹{abs(econ.profit_inr)/1e5:.1f}L daily {'profit' if econ.profit_inr>=0 else 'loss'}",
     "delta_pos": econ.profit_inr >= 0},
    {"label": "Break-Even LF", "value": f"{econ.belf*100:.1f}%", "sub": "Min load factor needed", "variant": "amber"},
    {"label": "LF Cushion",    "value": f"{econ.lf_cushion*100:+.1f}pp",
     "sub": f"{load_factor*100:.0f}% actual vs {econ.belf*100:.1f}% BELF",
     "variant": "positive" if econ.lf_cushion > 0 else "negative"},
])

# ── Charts ─────────────────────────────────────────────────────────────────────
section("Cost & Revenue Analysis")
ch1, ch2 = st.columns(2)

with ch1:
    costs = {"Fuel": econ.fuel_cost_inr, "Crew": econ.crew_cost_inr,
             "Maintenance": econ.maintenance_cost_inr,
             "Airport": econ.airport_cost_inr, "Overhead": econ.overhead_cost_inr}
    fig = go.Figure(go.Bar(
        x=list(costs.keys()), y=[v/1e5 for v in costs.values()],
        marker_color=[C["accent"],C["green"],C["amber"],C["red"],C["text3"]],
        marker_line_width=0,
        text=[f"₹{v/1e5:.1f}L" for v in costs.values()],
        textposition="outside", textfont=dict(size=11, color=C["text3"]),
    ))
    apply_theme(fig, "Daily Cost Breakdown  (₹ Lakhs)", 300)
    fig.update_layout(yaxis_title="₹ Lakhs", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with ch2:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Revenue", x=["Daily P&L"], y=[econ.total_revenue_inr/1e5],
                           marker_color=C["green"], marker_line_width=0,
                           text=f"₹{econ.total_revenue_inr/1e5:.1f}L", textposition="outside",
                           textfont=dict(size=11, color=C["green"])))
    fig2.add_trace(go.Bar(name="Total Cost", x=["Daily P&L"], y=[econ.total_cost_inr/1e5],
                           marker_color=C["red"], marker_line_width=0,
                           text=f"₹{econ.total_cost_inr/1e5:.1f}L", textposition="outside",
                           textfont=dict(size=11, color=C["red"])))
    pc = C["green"] if econ.profit_inr >= 0 else C["red"]
    fig2.add_annotation(text=f"Net: ₹{econ.profit_inr/1e5:.1f}L/day",
                         x=0, y=max(econ.total_revenue_inr, econ.total_cost_inr)/1e5*1.2,
                         font=dict(size=12, color=pc), showarrow=False, xanchor="center")
    apply_theme(fig2, "Revenue vs Total Cost", 300)
    fig2.update_layout(barmode="group")
    st.plotly_chart(fig2, use_container_width=True)

# ── BELF Curve ─────────────────────────────────────────────────────────────────
section("Break-Even Load Factor Curve")
lf_vals = [i/100 for i in range(40, 101)]
profits = [compute_route_economics(RouteInputs(
    origin, destination, airline, aircraft_type, daily_freq, lf,
    atf_price_inr_per_litre=atf, crew_cost_pct=crew_pct,
    maintenance_cost_per_fh=maint, airport_charges_per_sector=airport_ch,
    overhead_pct=overhead_pct, yield_inr_per_km=yield_inr,
)).profit_inr/1e5 for lf in lf_vals]

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=[lf*100 for lf in lf_vals], y=[min(p,0) for p in profits],
                           fill="tozeroy", fillcolor="rgba(220,38,38,0.07)",
                           mode="none", showlegend=False, hoverinfo="skip"))
fig3.add_trace(go.Scatter(x=[lf*100 for lf in lf_vals], y=[max(p,0) for p in profits],
                           fill="tozeroy", fillcolor="rgba(5,150,105,0.07)",
                           mode="none", showlegend=False, hoverinfo="skip"))
fig3.add_trace(go.Scatter(x=[lf*100 for lf in lf_vals], y=profits, mode="lines",
                           line=dict(color=C["accent"], width=2.5), showlegend=False,
                           hovertemplate="LF: %{x:.0f}%<br>₹%{y:.2f}L<extra></extra>"))
fig3.add_vline(x=econ.belf*100, line_dash="dash", line_color=C["red"], line_width=1.5,
               annotation_text=f"BELF {econ.belf*100:.1f}%",
               annotation_font=dict(color=C["red"], size=11))
fig3.add_vline(x=load_factor*100, line_dash="dash", line_color=C["green"], line_width=1.5,
               annotation_text=f"Current {load_factor*100:.0f}%",
               annotation_font=dict(color=C["green"], size=11))
fig3.add_hline(y=0, line_color=C["border"], line_width=1)
apply_theme(fig3, "Daily Profit (₹L) vs Load Factor", 280)
fig3.update_layout(xaxis_title="Load Factor (%)", yaxis_title="Daily Profit (₹ Lakhs)", showlegend=False)
st.plotly_chart(fig3, use_container_width=True)

# ── Save Scenario ──────────────────────────────────────────────────────────────
section("Save Scenario")
s1, s2 = st.columns([5, 1])
with s1:
    sc_name = st.text_input("Name",
                             value=f"{al_info['name']} · {origin}–{destination} · {load_factor*100:.0f}% LF",
                             placeholder="Name this scenario…", label_visibility="collapsed")
with s2:
    if st.button("Save", use_container_width=True):
        save_scenario(sc_name, vars(inputs), econ.to_dict())
        st.success(f"Saved: {sc_name}")
