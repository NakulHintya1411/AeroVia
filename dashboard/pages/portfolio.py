"""Portfolio Overview — route map, KPIs, DGCA upload."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from config.constants import INDIAN_AIRPORTS, AIRLINES, AIRCRAFT_TYPES
from economics.engine import RouteInputs, compute_route_economics
from ingestion.loader import load_dgca_file, generate_demo_data


def _get_or_init_data():
    if "portfolio_df" not in st.session_state:
        st.session_state.portfolio_df = None
    return st.session_state.portfolio_df


def render():
    st.title("🗺 Portfolio Overview")
    st.caption("Your route network at a glance — upload DGCA data or explore with demo routes.")

    # ── Data Source ───────────────────────────────────────────────────────────
    col_src, col_info = st.columns([2, 3])
    with col_src:
        data_mode = st.radio("Data Source", ["Demo Data", "Upload DGCA File"], horizontal=True)

    df = None
    warnings = []

    if data_mode == "Upload DGCA File":
        uploaded = st.file_uploader("Upload DGCA traffic CSV or Excel", type=["csv", "xlsx", "xls"])
        if uploaded:
            df, warnings = load_dgca_file(uploaded)
            if warnings:
                for w in warnings:
                    st.warning(w)
            if df.empty:
                st.error("Could not parse the file. Check format.")
                return
            st.success(f"Loaded {len(df):,} records from {uploaded.name}")

            # Column mapping UI if needed
            missing_cols = [c for c in ["origin", "destination", "airline_code"] if c not in df.columns]
            if missing_cols:
                st.markdown('<div class="section-header">Column Mapping</div>', unsafe_allow_html=True)
                st.caption("Map your file's columns to AeroVia fields:")
                remaps = {}
                for mc in missing_cols:
                    file_cols = ["(skip)"] + list(df.columns)
                    chosen = st.selectbox(f"Which column is '{mc}'?", file_cols, key=f"map_{mc}")
                    if chosen != "(skip)":
                        remaps[chosen] = mc
                if remaps:
                    df = df.rename(columns=remaps)
        else:
            st.info("Upload a DGCA CSV/Excel file above.")
            return
    else:
        df = generate_demo_data()
        st.caption("Showing synthetic demo data — 8 routes × 3 airlines × 12 months.")

    if df is None or df.empty:
        return

    st.session_state.portfolio_df = df

    # ── Compute economics for all unique routes ───────────────────────────────
    if "origin" in df.columns and "destination" in df.columns:
        routes = df[["origin", "destination"]].drop_duplicates()
        route_econs = []
        for _, row in routes.iterrows():
            if row["origin"] not in INDIAN_AIRPORTS or row["destination"] not in INDIAN_AIRPORTS:
                continue
            # Average LF from data if available
            subset = df[(df["origin"] == row["origin"]) & (df["destination"] == row["destination"])]
            avg_lf = subset["load_factor"].mean() if "load_factor" in df.columns else 0.80
            inp = RouteInputs(
                origin=row["origin"], destination=row["destination"],
                airline_code=subset["airline_code"].mode()[0] if "airline_code" in subset.columns else "6E",
                aircraft_type="A320", daily_frequency=3,
                load_factor=float(avg_lf) if not np.isnan(avg_lf) else 0.80,
            )
            econ = compute_route_economics(inp)
            route_econs.append({
                "route": f"{row['origin']}-{row['destination']}",
                "origin": row["origin"],
                "destination": row["destination"],
                **econ.to_dict(),
            })
        econ_df = pd.DataFrame(route_econs)
    else:
        econ_df = pd.DataFrame()

    # ── Summary KPIs ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Portfolio Summary</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)

    if not econ_df.empty:
        profitable = (econ_df["margin_pct"] > 0).sum()
        avg_margin = econ_df["margin_pct"].mean()
        avg_rask = econ_df["rask"].mean()
        avg_cask = econ_df["cask"].mean()
        total_routes = len(econ_df)

        def kpi_card(col, label, val):
            col.markdown(f"""<div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val}</div>
            </div>""", unsafe_allow_html=True)

        kpi_card(k1, "Total Routes", str(total_routes))
        kpi_card(k2, "Profitable Routes", f"{profitable}/{total_routes}")
        kpi_card(k3, "Avg Margin", f"{avg_margin:.1f}%")
        kpi_card(k4, "Avg RASK", f"{avg_rask:.1f}p")
        kpi_card(k5, "Avg CASK", f"{avg_cask:.1f}p")

    # ── Route Network Map ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Route Network Map</div>', unsafe_allow_html=True)

    fig = go.Figure()

    # Airport nodes
    ap_lat = [v["lat"] for v in INDIAN_AIRPORTS.values() if any(
        (econ_df["origin"] == k).any() or (econ_df["destination"] == k).any()
        for k in [list(INDIAN_AIRPORTS.keys())[list(INDIAN_AIRPORTS.values()).index(v)]]
    )] if not econ_df.empty else [v["lat"] for v in INDIAN_AIRPORTS.values()]

    # Plot route arcs
    if not econ_df.empty:
        for _, row in econ_df.iterrows():
            orig = INDIAN_AIRPORTS.get(row["origin"])
            dest = INDIAN_AIRPORTS.get(row["destination"])
            if not orig or not dest:
                continue
            color = "#34d399" if row["margin_pct"] > 2 else "#f87171" if row["margin_pct"] < 0 else "#fbbf24"
            fig.add_trace(go.Scattergeo(
                lon=[orig["lon"], dest["lon"]],
                lat=[orig["lat"], dest["lat"]],
                mode="lines",
                line=dict(width=2, color=color),
                opacity=0.7,
                showlegend=False,
                hoverinfo="skip",
            ))

        # Airport markers
        airports_in_use = set(econ_df["origin"].tolist() + econ_df["destination"].tolist())
        ap_data = [(k, v) for k, v in INDIAN_AIRPORTS.items() if k in airports_in_use]
        fig.add_trace(go.Scattergeo(
            lon=[v["lon"] for _, v in ap_data],
            lat=[v["lat"] for _, v in ap_data],
            mode="markers+text",
            marker=dict(size=10, color="#3b82f6", symbol="circle", line=dict(color="#1e40af", width=1)),
            text=[k for k, _ in ap_data],
            textposition="top center",
            textfont=dict(size=10, color="#93c5fd"),
            hovertext=[f"{k} — {v['city']}" for k, v in ap_data],
            hoverinfo="text",
            showlegend=False,
        ))

    # Legend items
    for label, color in [("Profitable", "#34d399"), ("Break-Even", "#fbbf24"), ("Loss", "#f87171")]:
        fig.add_trace(go.Scattergeo(lon=[None], lat=[None], mode="lines",
                                    line=dict(color=color, width=3), name=label))

    fig.update_layout(
        geo=dict(
            scope="asia",
            center=dict(lat=22, lon=82),
            projection_scale=4,
            showland=True, landcolor="#111c35",
            showocean=True, oceancolor="#0a0f1e",
            showcoastlines=True, coastlinecolor="#1e3058",
            showcountries=True, countrycolor="#1e3058",
            showlakes=False,
            bgcolor="#0a0f1e",
        ),
        paper_bgcolor="#0a0f1e",
        font_color="#c8d6f0",
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(bgcolor="#0d1426", bordercolor="#1e3058", font=dict(color="#c8d6f0")),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Route Margin Table ────────────────────────────────────────────────────
    if not econ_df.empty:
        st.markdown('<div class="section-header">Route Profitability Table</div>', unsafe_allow_html=True)

        # Filter controls
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            show_filter = st.selectbox("Filter", ["All Routes", "Profitable Only", "Loss-Making Only"])
        with fc2:
            sort_by = st.selectbox("Sort By", ["margin_pct", "rask", "cask", "belf", "distance_km"])
        with fc3:
            sort_dir = st.radio("Order", ["↓ Descending", "↑ Ascending"], horizontal=True)

        filtered = econ_df.copy()
        if show_filter == "Profitable Only":
            filtered = filtered[filtered["margin_pct"] > 0]
        elif show_filter == "Loss-Making Only":
            filtered = filtered[filtered["margin_pct"] < 0]

        filtered = filtered.sort_values(sort_by, ascending=(sort_dir == "↑ Ascending"))

        display_cols = ["route", "distance_km", "load_factor", "rask", "cask", "margin_pct", "belf", "profit_inr"]
        display_df = filtered[display_cols].copy()
        display_df.columns = ["Route", "Distance (km)", "Load Factor", "RASK (p)", "CASK (p)", "Margin %", "BELF", "Daily Profit (₹)"]
        display_df["Load Factor"] = display_df["Load Factor"].map("{:.1%}".format)
        display_df["BELF"] = display_df["BELF"].map("{:.1%}".format)
        display_df["Daily Profit (₹)"] = display_df["Daily Profit (₹)"].map("₹{:,.0f}".format)

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Export
        csv = filtered.to_csv(index=False)
        st.download_button("📥 Export Route Data CSV", csv, "aerovia_portfolio.csv", "text/csv")
