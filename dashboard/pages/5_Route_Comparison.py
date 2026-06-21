"""Route Comparison — compare up to 3 routes side by side."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · Route Comparison", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section, kpi_row, apply_theme, empty_state
from dashboard._shared.styles import COLORS
from dashboard.utils.auth import require_auth, show_user_menu
inject_css()
require_auth()

import plotly.graph_objects as go
import pandas as pd
from config.constants import (INDIAN_AIRPORTS, INTERNATIONAL_AIRPORTS, AIRLINES,
                               AIRCRAFT_TYPES, AIRLINE_FLEET, AIRLINE_AIRCRAFT,
                               DEFAULT_COST_ASSUMPTIONS, get_airline_airports,
                               get_airline_intl_airports)
from economics.engine import RouteInputs, compute_route_economics

with st.sidebar:
    sidebar_logo()
    show_user_menu()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>',
                unsafe_allow_html=True)

page_header(
    "Route Intelligence", "Route Comparison",
    "Compare up to 3 routes side by side — KPIs, cost breakdown, and profitability."
)
C = COLORS
ALL_AIRPORTS = {**INDIAN_AIRPORTS, **INTERNATIONAL_AIRPORTS}

# ── How many routes to compare ────────────────────────────────────────────────
section("Setup")
n_routes = st.radio("Number of routes to compare", [2, 3],
                     horizontal=True, label_visibility="collapsed")

# ── Build route configs ───────────────────────────────────────────────────────
route_configs = []
cols = st.columns(n_routes)

for i, col in enumerate(cols):
    with col:
        st.markdown(f'<div class="sec-label">Route {i+1}</div>', unsafe_allow_html=True)

        # Airline
        al_opts = {v["name"]: k for k, v in AIRLINES.items()}
        al_name = st.selectbox("Airline", list(al_opts.keys()),
                                key=f"cmp_al_{i}", label_visibility="collapsed",
                                index=i % len(al_opts))
        airline = al_opts[al_name]
        al_info = AIRLINES[airline]

        # Route type
        rt = st.radio("Type", ["Domestic", "International"],
                       horizontal=True, key=f"cmp_rt_{i}", label_visibility="collapsed")

        if rt == "Domestic":
            aps = get_airline_airports(airline)
            ap_opts = {f"{k} — {v['city']}": k
                       for k, v in sorted(aps.items(), key=lambda x: x[1]["city"])}
            orig = ap_opts[st.selectbox("Origin", list(ap_opts.keys()),
                                         key=f"cmp_o_{i}", label_visibility="collapsed")]
            dopts = {k: v for k, v in ap_opts.items() if v != orig}
            dest = dopts[st.selectbox("Destination", list(dopts.keys()),
                                       key=f"cmp_d_{i}", index=min(i+2, len(dopts)-1),
                                       label_visibility="collapsed")]
        else:
            aps_intl = get_airline_intl_airports(airline)
            if not aps_intl:
                st.caption("No international destinations for this airline.")
                route_configs.append(None)
                continue
            indian_hubs = {k: v for k, v in INDIAN_AIRPORTS.items()
                           if k in ["DEL", "BOM", "BLR", "MAA", "HYD", "CCU"]}
            orig_opts = {f"{k} — {v['city']}": k for k, v in indian_hubs.items()}
            dest_intl = {f"{k} — {v['city']}, {v['country']}": k
                         for k, v in sorted(aps_intl.items(), key=lambda x: x[1]["city"])}
            orig = orig_opts[st.selectbox("Origin Hub", list(orig_opts.keys()),
                                           key=f"cmp_o_{i}", label_visibility="collapsed")]
            dest = dest_intl[st.selectbox("Destination", list(dest_intl.keys()),
                                           key=f"cmp_d_{i}", label_visibility="collapsed")]

        # Aircraft
        fleet = AIRLINE_FLEET.get(airline, list(AIRCRAFT_TYPES.keys()))
        default_ac = AIRLINE_AIRCRAFT.get(airline, fleet[0])
        ac_idx = fleet.index(default_ac) if default_ac in fleet else 0
        aircraft = st.selectbox("Aircraft", fleet, index=ac_idx,
                                 key=f"cmp_ac_{i}", label_visibility="collapsed")

        # Operations
        lf = st.slider("Load Factor %", 40, 100, 82, key=f"cmp_lf_{i}") / 100
        freq = st.number_input("Flights/day", 1, 30, 3, key=f"cmp_freq_{i}")

        route_configs.append({
            "airline": airline,
            "al_info": al_info,
            "origin": orig,
            "destination": dest,
            "aircraft": aircraft,
            "lf": lf,
            "freq": freq,
            "label": f"{al_info['name']}\n{orig}→{dest}"
        })

# ── Compute all routes ────────────────────────────────────────────────────────
valid_configs = [r for r in route_configs if r]
if len(valid_configs) < 2:
    empty_state("⚖", "Add at least 2 routes", "Configure routes above to start comparing.")
    st.stop()

results = []
for cfg in valid_configs:
    inp = RouteInputs(
        origin=cfg["origin"], destination=cfg["destination"],
        airline_code=cfg["airline"], aircraft_type=cfg["aircraft"],
        daily_frequency=cfg["freq"], load_factor=cfg["lf"],
        atf_price_inr_per_litre=DEFAULT_COST_ASSUMPTIONS["atf_price_inr_per_litre"],
        yield_inr_per_km=DEFAULT_COST_ASSUMPTIONS["avg_yield_inr_per_km"],
    )
    econ = compute_route_economics(inp)
    results.append({"config": cfg, "econ": econ})

# ── KPI comparison cards ──────────────────────────────────────────────────────
section("Head-to-Head Comparison")

metrics = [
    ("RASK (p/ASK)",    lambda e: f"{e.rask:.1f}p",           lambda e: e.rask),
    ("CASK (p/ASK)",    lambda e: f"{e.cask:.1f}p",           lambda e: -e.cask),   # lower is better
    ("Net Margin",      lambda e: f"{e.margin_pct:.1f}%",     lambda e: e.margin_pct),
    ("Break-Even LF",   lambda e: f"{e.belf*100:.1f}%",       lambda e: -e.belf),   # lower is better
    ("LF Cushion",      lambda e: f"{e.lf_cushion*100:+.1f}pp", lambda e: e.lf_cushion),
    ("Daily Profit",    lambda e: f"₹{e.profit_inr/1e5:.1f}L", lambda e: e.profit_inr),
    ("Distance",        lambda e: f"{e.distance_km:,.0f} km", lambda e: None),
    ("Flight Time",     lambda e: f"{e.flight_time_hr:.1f} hr", lambda e: None),
]

for label, fmt, rank_fn in metrics:
    st.markdown(f'<div class="sec-label" style="margin:16px 0 8px">{label}</div>',
                unsafe_allow_html=True)
    m_cols = st.columns(len(results))

    # Determine best
    if rank_fn(results[0]["econ"]) is not None:
        scores = [rank_fn(r["econ"]) for r in results]
        best_idx = scores.index(max(scores))
    else:
        best_idx = -1

    for j, (col, res) in enumerate(zip(m_cols, results)):
        cfg, econ = res["config"], res["econ"]
        is_best = j == best_idx
        badge_cls = "badge-profit" if econ.margin_pct > 2 else \
                    "badge-loss" if econ.margin_pct < 0 else "badge-break"
        variant = "positive" if is_best and rank_fn(econ) is not None else ""
        col.markdown(f"""
        <div class="kpi-card {'kv-positive' if is_best and rank_fn(econ) is not None else ''}">
          <div class="kpi-label" style="color:{cfg['al_info']['color']};font-weight:700">
            {cfg['al_info']['name']}
          </div>
          <div style="font-size:11px;color:var(--text-3);margin-bottom:6px">
            {cfg['origin']} → {cfg['destination']}
          </div>
          <div class="kpi-value">{fmt(econ)}</div>
          {"<div style='margin-top:6px;font-size:10px;color:var(--green);font-weight:600'>▲ Best</div>" if is_best and rank_fn(econ) is not None else ""}
        </div>
        """, unsafe_allow_html=True)

# ── Visual chart comparison ────────────────────────────────────────────────────
section("Cost Breakdown Comparison")

fig = go.Figure()
cost_labels = ["Fuel", "Crew", "Maintenance", "Airport", "Overhead"]
colors_cost = [C["accent"], C["green"], C["amber"], C["red"], C["text3"]]

for res in results:
    cfg, econ = res["config"], res["econ"]
    label = f"{cfg['al_info']['name']} · {cfg['origin']}→{cfg['destination']}"
    costs = [econ.fuel_cost_inr, econ.crew_cost_inr, econ.maintenance_cost_inr,
             econ.airport_cost_inr, econ.overhead_cost_inr]
    fig.add_trace(go.Bar(
        name=label,
        x=cost_labels,
        y=[c/1e5 for c in costs],
        text=[f"₹{c/1e5:.1f}L" for c in costs],
        textposition="outside",
        textfont=dict(size=9, color=C["text3"]),
    ))

apply_theme(fig, "Daily Cost Breakdown per Route  (₹ Lakhs)", 360)
fig.update_layout(barmode="group", yaxis_title="₹ Lakhs")
st.plotly_chart(fig, use_container_width=True)

# ── RASK vs CASK scatter ───────────────────────────────────────────────────────
section("RASK vs CASK  —  above the diagonal is profitable")
fig2 = go.Figure()

for res in results:
    cfg, econ = res["config"], res["econ"]
    label = f"{cfg['al_info']['name']} · {cfg['origin']}→{cfg['destination']}"
    color = C["green"] if econ.margin_pct > 0 else C["red"]
    fig2.add_trace(go.Scatter(
        x=[econ.cask], y=[econ.rask],
        mode="markers+text",
        marker=dict(size=18, color=cfg["al_info"]["color"],
                    line=dict(color=C["border"], width=1.5)),
        text=[f"{cfg['origin']}→{cfg['destination']}"],
        textposition="top center",
        textfont=dict(size=10, color=C["text2"]),
        name=label,
        hovertemplate=f"{label}<br>RASK: {econ.rask:.1f}p | CASK: {econ.cask:.1f}p | Margin: {econ.margin_pct:.1f}%<extra></extra>",
    ))

all_vals = [r["econ"].cask for r in results] + [r["econ"].rask for r in results]
lo, hi = min(all_vals)*0.88, max(all_vals)*1.12
fig2.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines",
                           line=dict(color=C["amber"], dash="dash", width=1.5),
                           name="Break-Even Line"))
apply_theme(fig2, "RASK vs CASK Scatter", 380)
fig2.update_layout(xaxis_title="CASK (p/ASK)", yaxis_title="RASK (p/ASK)")
st.plotly_chart(fig2, use_container_width=True)

# ── Summary table ──────────────────────────────────────────────────────────────
section("Full Comparison Table")
rows = []
for res in results:
    cfg, econ = res["config"], res["econ"]
    rows.append({
        "Airline":       cfg["al_info"]["name"],
        "Route":         f"{cfg['origin']} → {cfg['destination']}",
        "Aircraft":      cfg["aircraft"],
        "Distance":      f"{econ.distance_km:,.0f} km",
        "Flight Time":   f"{econ.flight_time_hr:.1f} hr",
        "Load Factor":   f"{cfg['lf']:.0%}",
        "RASK (p)":      f"{econ.rask:.1f}",
        "CASK (p)":      f"{econ.cask:.1f}",
        "Margin %":      f"{econ.margin_pct:.1f}%",
        "BELF":          f"{econ.belf:.1%}",
        "LF Cushion":    f"{econ.lf_cushion:+.1%}",
        "Daily Revenue": f"₹{econ.total_revenue_inr/1e5:.1f}L",
        "Daily Cost":    f"₹{econ.total_cost_inr/1e5:.1f}L",
        "Daily Profit":  f"₹{econ.profit_inr/1e5:.1f}L",
    })

cdf = pd.DataFrame(rows).set_index("Airline")
st.dataframe(cdf, use_container_width=True)
st.download_button("↓ Export Comparison CSV", cdf.to_csv(),
                    "aerovia_comparison.csv", "text/csv")
