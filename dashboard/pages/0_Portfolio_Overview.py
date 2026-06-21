"""AeroVia — Portfolio Overview."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · Portfolio", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section, kpi_row, empty_state, apply_theme
from dashboard._shared.styles import COLORS
from dashboard.utils.auth import require_auth, show_user_menu
inject_css()
require_auth()

import plotly.graph_objects as go
import pandas as pd, numpy as np, io, os
from config.constants import INDIAN_AIRPORTS, AIRLINES, get_airline_airports, AIRLINE_AIRCRAFT
from economics.engine import RouteInputs, compute_route_economics
from ingestion.loader import load_dgca_file

with st.sidebar:
    sidebar_logo()
    show_user_menu()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>',
                unsafe_allow_html=True)

page_header(
    "Network Intelligence", "Portfolio Overview",
    "Select an airline and load traffic data to visualise your route network."
)
C = COLORS

# ── Airline selector ──────────────────────────────────────────────────────────
section("Select Airline")
al_cols = st.columns(len(AIRLINES))
for i, (code, info) in enumerate(AIRLINES.items()):
    with al_cols[i]:
        if st.button(info["name"], key=f"pal_{code}", use_container_width=True,
                     help=f"{info['name']} · {info['type']}"):
            st.session_state["portfolio_airline"] = code
            st.rerun()

airline = st.session_state.get("portfolio_airline")

if not airline:
    empty_state(
        "✈",
        "Select an airline to get started",
        "Choose from IndiGo, Air India, Air India Express, Akasa Air, or SpiceJet above. "
        "Then load sample data or upload your own DGCA traffic file.",
        "← Pick an airline above"
    )
    st.stop()

al_info = AIRLINES[airline]
st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;margin:8px 0 16px">
  <div style="background:{al_info['color']};color:#fff;padding:5px 14px;
              border-radius:20px;font-size:12px;font-weight:700">
    {al_info['name']} · {al_info['type']}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Data source ────────────────────────────────────────────────────────────────
section("Traffic Data")
d1, d2 = st.columns([1, 2])
with d1:
    data_mode = st.radio("Source", ["Load Sample Data", "Upload DGCA File"],
                          label_visibility="collapsed")
with d2:
    if data_mode == "Load Sample Data":
        st.markdown('<div class="info-panel">Pre-loaded with realistic Indian domestic traffic data — 22 routes · 5 airlines · 12 months. Calibrated to real aviation economics including loss-making UDAN routes.</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-panel">Upload a DGCA monthly or annual traffic CSV/Excel. AeroVia auto-detects column names — use the mapper if needed.</div>',
                    unsafe_allow_html=True)

df = None

if data_mode == "Load Sample Data":
    # Load bundled sample data
    sample_path = os.path.join(_root, "data", "sample_dgca_traffic.csv")
    if os.path.exists(sample_path):
        df = pd.read_csv(sample_path)
        df.columns = [c.lower() for c in df.columns]
        # Rename to match expected format
        df = df.rename(columns={
            "airline_code": "airline_code",
            "origin": "origin",
            "destination": "destination",
            "load_factor": "load_factor",
        })
        # Filter to selected airline if available, else show all
        if airline in df["airline_code"].values:
            df = df[df["airline_code"] == airline].copy()
        st.caption(f"Showing {len(df):,} records for {al_info['name']} · FY2024")

        # Also offer download of sample file
        with open(sample_path, "rb") as f:
            st.download_button(
                "↓ Download Sample DGCA File",
                f.read(),
                "aerovia_sample_dgca.csv",
                "text/csv",
                help="Download this sample file to see the expected format for your own DGCA data"
            )
    else:
        st.error("Sample data file not found. Please upload a DGCA file instead.")
        st.stop()

else:
    uploaded = st.file_uploader(
        "Drop your DGCA file here — CSV or Excel",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )
    if not uploaded:
        empty_state(
            "📂",
            "No file uploaded yet",
            "Upload a DGCA traffic file above to see your route network map and profitability analysis.",
            "Accepted: CSV · Excel (.xlsx / .xls)"
        )
        st.stop()

    df, warnings = load_dgca_file(uploaded)
    for w in warnings:
        st.warning(w)
    if df.empty:
        st.error("Could not parse the file. Check the format and try again.")
        st.stop()
    st.success(f"{len(df):,} records loaded from **{uploaded.name}**")

    missing = [c for c in ["origin", "destination", "airline_code"] if c not in df.columns]
    if missing:
        section("Column Mapping")
        st.caption("Some columns couldn't be auto-detected. Map them below:")
        for mc in missing:
            chosen = st.selectbox(f"Which column is '{mc}'?",
                                   ["(skip)"] + list(df.columns), key=f"map_{mc}")
            if chosen != "(skip)":
                df = df.rename(columns={chosen: mc})

if df is None or df.empty:
    st.stop()

# ── Compute economics ─────────────────────────────────────────────────────────
default_ac = AIRLINE_AIRCRAFT.get(airline, "A320neo")
econ_rows = []

for _, row in df[["origin", "destination"]].drop_duplicates().iterrows():
    if row["origin"] not in INDIAN_AIRPORTS or row["destination"] not in INDIAN_AIRPORTS:
        continue
    sub = df[(df["origin"] == row["origin"]) & (df["destination"] == row["destination"])]
    avg_lf = sub["load_factor"].mean() if "load_factor" in df.columns else 0.80
    if pd.isna(avg_lf): avg_lf = 0.80
    avg_yield_factor = sub["_yield_factor"].mean() if "_yield_factor" in sub.columns else 1.0
    yield_inr = 4.2 * float(avg_yield_factor)
    e = compute_route_economics(RouteInputs(
        row["origin"], row["destination"], airline, default_ac, 3,
        float(avg_lf), yield_inr_per_km=yield_inr
    ))
    econ_rows.append({
        "route": f"{row['origin']} – {row['destination']}",
        "origin": row["origin"], "destination": row["destination"],
        **e.to_dict()
    })

econ_df = pd.DataFrame(econ_rows)

if econ_df.empty:
    empty_state(
        "🗺",
        "No matching routes found",
        "The data doesn't contain routes within the known Indian airport network. "
        "Check that origin/destination columns contain IATA codes (e.g. DEL, BOM, BLR)."
    )
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
section("Network Summary")
n = len(econ_df)
p = (econ_df["margin_pct"] > 0).sum()
l = (econ_df["margin_pct"] < 0).sum()
kpi_row([
    {"label": "Routes Analysed",  "value": str(n), "variant": "accent"},
    {"label": "Profitable",       "value": f"{p}/{n}",
     "variant": "positive" if n > 0 and p/n >= 0.6 else "negative"},
    {"label": "Loss-Making",      "value": str(l),
     "variant": "negative" if l > 0 else ""},
    {"label": "Avg Net Margin",   "value": f"{econ_df['margin_pct'].mean():.1f}%",
     "variant": "positive" if econ_df["margin_pct"].mean() > 0 else "negative"},
    {"label": "Avg RASK",         "value": f"{econ_df['rask'].mean():.1f}p"},
])

# ── Map ───────────────────────────────────────────────────────────────────────
section(f"{al_info['name']} Route Network")
fig = go.Figure()

for _, row in econ_df.iterrows():
    orig = INDIAN_AIRPORTS.get(row["origin"])
    dest = INDIAN_AIRPORTS.get(row["destination"])
    if not orig or not dest: continue
    color = C["green"] if row["margin_pct"] > 2 else C["red"] if row["margin_pct"] < 0 else C["amber"]
    fig.add_trace(go.Scattergeo(
        lon=[orig["lon"], dest["lon"]], lat=[orig["lat"], dest["lat"]],
        mode="lines", line=dict(width=2, color=color),
        opacity=0.65, showlegend=False,
        hovertext=f"{row['route']}<br>Margin: {row['margin_pct']:.1f}%",
        hoverinfo="text"
    ))

in_use = set(econ_df["origin"].tolist() + econ_df["destination"].tolist())
ap_data = [(k, v) for k, v in INDIAN_AIRPORTS.items() if k in in_use]
if ap_data:
    fig.add_trace(go.Scattergeo(
        lon=[v["lon"] for _, v in ap_data],
        lat=[v["lat"] for _, v in ap_data],
        mode="markers+text",
        marker=dict(size=9, color=al_info["color"], line=dict(color="#ffffff", width=1.5)),
        text=[k for k, _ in ap_data], textposition="top center",
        textfont=dict(size=9, color=C["text2"]),
        hovertext=[f"{k} — {v['city']}" for k, v in ap_data],
        hoverinfo="text", showlegend=False,
    ))

for label, color in [("Profitable", C["green"]),
                      ("Break-Even", C["amber"]),
                      ("Loss-Making", C["red"])]:
    fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode="lines",
                                 line=dict(color=color, width=2.5), name=label))

fig.update_layout(
    geo=dict(scope="asia", center=dict(lat=22, lon=82), projection_scale=4.2,
             showland=True, landcolor="#f1f4f9", showocean=True, oceancolor="#e8edf5",
             showcoastlines=True, coastlinecolor="#c8d0e2",
             showcountries=True, countrycolor="#c8d0e2", showlakes=False, bgcolor="#ffffff"),
    paper_bgcolor="#ffffff",
    font=dict(color=C["text3"], family="Inter, sans-serif", size=10),
    height=500, margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(bgcolor="#ffffff", bordercolor=C["border"],
                font=dict(color=C["text3"], size=11)),
)
st.plotly_chart(fig, use_container_width=True)

# ── Table ─────────────────────────────────────────────────────────────────────
section("Route Profitability Table")
f1, f2, f3 = st.columns(3)
with f1:
    show = st.selectbox("Filter", ["All Routes", "Profitable Only", "Loss-Making Only"],
                         label_visibility="collapsed")
with f2:
    sort_by = st.selectbox("Sort by",
                            ["margin_pct", "rask", "cask", "belf", "distance_km"],
                            label_visibility="collapsed")
with f3:
    asc = st.radio("Order", ["↓ Desc", "↑ Asc"], horizontal=True,
                    label_visibility="collapsed") == "↑ Asc"

filt = econ_df.copy()
if show == "Profitable Only":    filt = filt[filt["margin_pct"] > 0]
elif show == "Loss-Making Only": filt = filt[filt["margin_pct"] < 0]
filt = filt.sort_values(sort_by, ascending=asc)

disp = filt[["route", "distance_km", "load_factor", "rask", "cask",
              "margin_pct", "belf", "profit_inr"]].copy()
disp.columns = ["Route", "Dist (km)", "Load Factor", "RASK (p)",
                 "CASK (p)", "Margin %", "BELF", "Daily Profit"]
disp["Load Factor"]  = disp["Load Factor"].map("{:.1%}".format)
disp["BELF"]         = disp["BELF"].map("{:.1%}".format)
disp["Daily Profit"] = disp["Daily Profit"].map("₹{:,.0f}".format)
st.dataframe(disp, use_container_width=True, hide_index=True)
st.download_button("↓ Export CSV", filt.to_csv(index=False),
                    f"aerovia_{airline}_portfolio.csv", "text/csv")
