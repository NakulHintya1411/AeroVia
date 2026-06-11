"""AeroVia — Portfolio Overview (home page)."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · Portfolio", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section, kpi_row, apply_theme
from dashboard._shared.styles import COLORS
inject_css()

import plotly.graph_objects as go
import pandas as pd, numpy as np
from config.constants import INDIAN_AIRPORTS, AIRLINES, AIRLINE_DESTINATIONS, get_airline_airports
from economics.engine import RouteInputs, compute_route_economics
from ingestion.loader import load_dgca_file, generate_demo_data

with st.sidebar:
    sidebar_logo()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>', unsafe_allow_html=True)

page_header("Network Intelligence", "Portfolio Overview",
            "Select an airline to explore its route network, or upload DGCA data for custom analysis.")

C = COLORS

# ── Airline selector ──────────────────────────────────────────────────────────
section("Select Airline")
al_cols = st.columns(len(AIRLINES))
for i, (code, info) in enumerate(AIRLINES.items()):
    with al_cols[i]:
        if st.button(f"{info['name']}\n{info['type']}", key=f"al_{code}", use_container_width=True):
            st.session_state["portfolio_airline"] = code
            st.rerun()

if "portfolio_airline" not in st.session_state:
    st.session_state["portfolio_airline"] = "6E"

airline = st.session_state["portfolio_airline"]
al_info = AIRLINES[airline]
dest_count = len(AIRLINE_DESTINATIONS.get(airline, {}).get("domestic", []))

st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;margin:8px 0 16px">
  <div style="background:{al_info['color']};color:#fff;padding:5px 14px;
              border-radius:20px;font-size:12px;font-weight:700">
    {al_info['name']} · {al_info['type']}
  </div>
  <span style="font-size:12px;color:var(--text-3)">{dest_count} domestic destinations</span>
</div>
""", unsafe_allow_html=True)

# ── Data source ────────────────────────────────────────────────────────────────
section("Data Source")
c1, c2 = st.columns([1, 2])
with c1:
    mode = st.radio("Source", ["Airline Network", "Upload DGCA File"], label_visibility="collapsed")
with c2:
    if mode == "Airline Network":
        st.markdown(f'<div class="info-panel">Showing all {dest_count} domestic destinations for {al_info["name"]}. Economics modelled with industry-standard assumptions.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-panel">Upload DGCA monthly CSV or Excel. AeroVia auto-detects columns and provides a mapping UI if needed.</div>', unsafe_allow_html=True)

df = None
if mode == "Upload DGCA File":
    uploaded = st.file_uploader("Drop DGCA file (CSV or Excel)", type=["csv","xlsx","xls"], label_visibility="collapsed")
    if uploaded:
        df, warnings = load_dgca_file(uploaded)
        for w in warnings: st.warning(w)
        if df.empty: st.error("Could not parse file."); st.stop()
        st.success(f"{len(df):,} records loaded")
        missing = [c for c in ["origin","destination","airline_code"] if c not in df.columns]
        if missing:
            section("Column Mapping")
            for mc in missing:
                chosen = st.selectbox(f"Map → '{mc}'", ["(skip)"]+list(df.columns), key=f"map_{mc}")
                if chosen != "(skip)": df = df.rename(columns={chosen: mc})
    else:
        st.stop()
else:
    # Build route pairs from airline destinations
    aps = get_airline_airports(airline)
    codes = list(aps.keys())
    rows = []
    # Create representative route pairs (hub-and-spoke style sample)
    hubs = {"6E":["DEL","BOM","BLR"], "IX":["DEL","BOM","COK"],
            "AI":["DEL","BOM","BLR"], "QP":["DEL","BOM","BLR"], "SG":["DEL","BOM"]}
    hub_list = hubs.get(airline, codes[:3])
    seen = set()
    for hub in hub_list:
        if hub not in codes: continue
        for dest in codes:
            if dest == hub: continue
            pair = tuple(sorted([hub, dest]))
            if pair in seen: continue
            seen.add(pair)
            rows.append({"origin": hub, "destination": dest,
                          "airline_code": airline,
                          "load_factor": round(np.random.uniform(0.72, 0.88), 3)})
    df = pd.DataFrame(rows)

if df is None or df.empty: st.stop()

# ── Compute economics ─────────────────────────────────────────────────────────
from config.constants import AIRLINE_AIRCRAFT
default_ac = AIRLINE_AIRCRAFT.get(airline, "A320")
np.random.seed(42)
econ_rows = []
for _, row in df[["origin","destination"]].drop_duplicates().iterrows():
    if row["origin"] not in INDIAN_AIRPORTS or row["destination"] not in INDIAN_AIRPORTS: continue
    sub = df[(df["origin"]==row["origin"]) & (df["destination"]==row["destination"])]
    avg_lf = sub["load_factor"].mean() if "load_factor" in df.columns else 0.80
    if pd.isna(avg_lf): avg_lf = 0.80
    e = compute_route_economics(RouteInputs(
        row["origin"], row["destination"], airline, default_ac, 3, float(avg_lf)))
    econ_rows.append({"route": f"{row['origin']} – {row['destination']}",
                       "origin": row["origin"], "destination": row["destination"], **e.to_dict()})
econ_df = pd.DataFrame(econ_rows)

# ── KPIs ───────────────────────────────────────────────────────────────────────
if not econ_df.empty:
    section("Network Summary")
    n = len(econ_df)
    p = (econ_df["margin_pct"] > 0).sum()
    kpi_row([
        {"label": "Routes Modelled", "value": str(n), "variant": "accent"},
        {"label": "Profitable",      "value": f"{p}/{n}",
         "variant": "positive" if p/n >= 0.6 else "negative"},
        {"label": "Avg Net Margin",  "value": f"{econ_df['margin_pct'].mean():.1f}%",
         "variant": "positive" if econ_df["margin_pct"].mean() > 0 else "negative"},
        {"label": "Avg RASK",        "value": f"{econ_df['rask'].mean():.1f}p"},
        {"label": "Avg CASK",        "value": f"{econ_df['cask'].mean():.1f}p"},
    ])

# ── Map ────────────────────────────────────────────────────────────────────────
section(f"{al_info['name']} Route Network")
fig = go.Figure()
if not econ_df.empty:
    for _, row in econ_df.iterrows():
        orig = INDIAN_AIRPORTS.get(row["origin"]); dest = INDIAN_AIRPORTS.get(row["destination"])
        if not orig or not dest: continue
        color = C["green"] if row["margin_pct"] > 2 else C["red"] if row["margin_pct"] < 0 else C["amber"]
        fig.add_trace(go.Scattergeo(
            lon=[orig["lon"],dest["lon"]], lat=[orig["lat"],dest["lat"]],
            mode="lines", line=dict(width=1.5, color=color),
            opacity=0.55, showlegend=False, hoverinfo="skip"))

    in_use = set(econ_df["origin"].tolist()+econ_df["destination"].tolist())
    ap_data = [(k,v) for k,v in INDIAN_AIRPORTS.items() if k in in_use]
    fig.add_trace(go.Scattergeo(
        lon=[v["lon"] for _,v in ap_data], lat=[v["lat"] for _,v in ap_data],
        mode="markers+text",
        marker=dict(size=8, color=al_info["color"], line=dict(color="#ffffff", width=1.5)),
        text=[k for k,_ in ap_data], textposition="top center",
        textfont=dict(size=9, color=C["text2"]),
        hovertext=[f"{k} — {v['city']}" for k,v in ap_data],
        hoverinfo="text", showlegend=False))

for label, color in [("Profitable",C["green"]),("Break-Even",C["amber"]),("Loss-Making",C["red"])]:
    fig.add_trace(go.Scattergeo(lon=[None],lat=[None],mode="lines",
                                 line=dict(color=color,width=2.5),name=label))

fig.update_layout(
    geo=dict(scope="asia", center=dict(lat=22,lon=82), projection_scale=4.2,
             showland=True, landcolor="#f1f4f9", showocean=True, oceancolor="#e8edf5",
             showcoastlines=True, coastlinecolor="#c8d0e2",
             showcountries=True, countrycolor="#c8d0e2", showlakes=False, bgcolor="#ffffff"),
    paper_bgcolor="#ffffff",
    font=dict(color=C["text3"],family="Inter, sans-serif",size=10),
    height=500, margin=dict(l=0,r=0,t=0,b=0),
    legend=dict(bgcolor="#ffffff",bordercolor=C["border"],
                font=dict(color=C["text3"],size=11)),
)
st.plotly_chart(fig, use_container_width=True)

# ── Route Table ────────────────────────────────────────────────────────────────
if not econ_df.empty:
    section("Route Profitability Table")
    f1,f2,f3 = st.columns(3)
    with f1: show = st.selectbox("Filter", ["All","Profitable","Loss-Making"], label_visibility="collapsed")
    with f2: sort_by = st.selectbox("Sort by", ["margin_pct","rask","cask","belf","distance_km"], label_visibility="collapsed")
    with f3: asc = st.radio("Order", ["↓ Desc","↑ Asc"], horizontal=True, label_visibility="collapsed") == "↑ Asc"

    filt = econ_df.copy()
    if show == "Profitable": filt = filt[filt["margin_pct"]>0]
    elif show == "Loss-Making": filt = filt[filt["margin_pct"]<0]
    filt = filt.sort_values(sort_by, ascending=asc)

    disp = filt[["route","distance_km","load_factor","rask","cask","margin_pct","belf","profit_inr"]].copy()
    disp.columns = ["Route","Dist (km)","Load Factor","RASK (p)","CASK (p)","Margin %","BELF","Daily Profit"]
    disp["Load Factor"] = disp["Load Factor"].map("{:.1%}".format)
    disp["BELF"] = disp["BELF"].map("{:.1%}".format)
    disp["Daily Profit"] = disp["Daily Profit"].map("₹{:,.0f}".format)
    st.dataframe(disp, use_container_width=True, hide_index=True)
    st.download_button("↓ Export CSV", filt.to_csv(index=False), f"aerovia_{airline}_portfolio.csv", "text/csv")
