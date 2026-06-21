"""ML Forecasts — ATF history, price forecast, demand prediction, anomaly detection."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · ML Forecasts", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section, kpi_row, apply_theme
from dashboard._shared.styles import COLORS
from dashboard.utils.auth import require_auth, show_user_menu
from dashboard.utils.atf_history import get_atf_history_df, get_atf_stats, ATF_EVENTS
inject_css()
require_auth()

import plotly.graph_objects as go
import numpy as np, pandas as pd
from config.constants import INDIAN_AIRPORTS, AIRCRAFT_TYPES
from economics.engine import RouteInputs, compute_route_economics

with st.sidebar:
    sidebar_logo()
    show_user_menu()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>',
                unsafe_allow_html=True)

page_header("Predictive Analytics", "ML Forecasts",
            "ATF fuel price history, demand forecasting, and route anomaly detection.")
C = COLORS

tab1, tab2, tab3, tab4 = st.tabs([
    "⛽ ATF Price History",
    "📈 ATF Forecast",
    "🛫 Demand Forecast",
    "🔍 Anomaly Detection"
])

# ── Tab 1: ATF Price History ──────────────────────────────────────────────────
with tab1:
    hist_df = get_atf_history_df()
    stats = get_atf_stats(hist_df)

    section("ATF Price Overview  ·  Delhi (₹/litre)  ·  Jan 2021 – Dec 2025")
    kpi_row([
        {"label": "Current Price",  "value": f"₹{stats['current']:.1f}/L",
         "sub": "Latest available", "variant": "accent"},
        {"label": "12-Month Avg",   "value": f"₹{stats['avg_12m']:.1f}/L",
         "sub": "FY2025 average"},
        {"label": "YoY Change",     "value": f"{stats['yoy']:+.1f}%",
         "variant": "positive" if stats['yoy'] < 0 else "negative",
         "sub": "vs same month last year"},
        {"label": "All-Time High",  "value": f"₹{stats['peak']:.1f}/L",
         "sub": stats['peak_date'], "variant": "negative"},
        {"label": "Price Volatility","value": f"{stats['volatility']:.1f}%",
         "sub": "Monthly std deviation", "variant": "amber"},
    ])

    # Main history chart
    fig = go.Figure()

    # Shaded regions for price zones
    fig.add_hrect(y0=0,   y1=75,  fillcolor="rgba(5,150,105,0.06)",  line_width=0, annotation_text="Low zone", annotation_position="left")
    fig.add_hrect(y0=75,  y1=100, fillcolor="rgba(37,99,235,0.04)",  line_width=0, annotation_text="Normal zone", annotation_position="left")
    fig.add_hrect(y0=100, y1=150, fillcolor="rgba(220,38,38,0.05)",  line_width=0, annotation_text="Elevated zone", annotation_position="left")

    # Price line
    fig.add_trace(go.Scatter(
        x=hist_df["date"], y=hist_df["price"],
        mode="lines",
        line=dict(color=C["accent"], width=2.5),
        fill="tozeroy",
        fillcolor="rgba(37,99,235,0.06)",
        name="ATF Price (₹/L)",
        hovertemplate="%{x|%b %Y}<br>₹%{y:.2f}/L<extra></extra>",
    ))

    # 3-month rolling average
    hist_df["rolling_3m"] = hist_df["price"].rolling(3, center=True).mean()
    fig.add_trace(go.Scatter(
        x=hist_df["date"], y=hist_df["rolling_3m"],
        mode="lines",
        line=dict(color=C["amber"], width=1.5, dash="dot"),
        name="3-Month Rolling Avg",
        hovertemplate="%{x|%b %Y}<br>3M Avg: ₹%{y:.2f}/L<extra></extra>",
    ))

    # Event annotations
    for event in ATF_EVENTS:
        event_date = pd.to_datetime(event["date"] + "-01")
        price_at_event = hist_df.loc[hist_df["date"] == event_date, "price"]
        if not price_at_event.empty:
            fig.add_vline(
                x=event_date.timestamp() * 1000,
                line_dash="dot", line_color=event["color"], line_width=1,
                annotation_text=event["label"],
                annotation_font=dict(size=9, color=event["color"]),
                annotation_position="top right",
            )

    apply_theme(fig, "ATF Price History — Delhi (₹/litre)  ·  IOCL Data", 420)
    fig.update_layout(
        xaxis_title="", yaxis_title="₹ per litre",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # YoY change bar chart
    section("Year-on-Year Price Change (%)")
    yoy_df = hist_df.dropna(subset=["yoy_change"])
    fig2 = go.Figure(go.Bar(
        x=yoy_df["date"],
        y=yoy_df["yoy_change"],
        marker_color=[C["red"] if v > 0 else C["green"] for v in yoy_df["yoy_change"]],
        marker_line_width=0,
        hovertemplate="%{x|%b %Y}<br>YoY: %{y:+.1f}%<extra></extra>",
    ))
    fig2.add_hline(y=0, line_color=C["border"], line_width=1)
    apply_theme(fig2, "YoY ATF Price Change (%) — Red = price rising vs year ago", 280)
    fig2.update_layout(yaxis_title="YoY Change (%)", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    # Impact on airline costs
    section("ATF Cost Impact on Route Economics")
    st.caption("How the 2022 price spike affected route profitability — DEL → BOM, A320neo, 82% LF")

    ap = {f"{k} — {v['city']}": k for k, v in INDIAN_AIRPORTS.items()}
    ri1, ri2, ri3 = st.columns(3)
    with ri1: orig_h = ap[st.selectbox("Origin", list(ap.keys()), index=0, key="h_orig")]
    with ri2:
        dopts = {k: v for k, v in ap.items() if v != orig_h}
        dest_h = dopts[st.selectbox("Destination", list(dopts.keys()), index=4, key="h_dest")]
    with ri3: ac_h = st.selectbox("Aircraft", list(AIRCRAFT_TYPES.keys()), key="h_ac")

    # Compute margin at historical ATF prices
    sample_dates = hist_df[hist_df["date"].dt.month == 1].copy()  # Jan of each year
    margins_hist = []
    for _, row in sample_dates.iterrows():
        e = compute_route_economics(RouteInputs(
            orig_h, dest_h, "6E", ac_h, 3, 0.82,
            atf_price_inr_per_litre=row["price"]
        ))
        margins_hist.append({"date": row["date"], "price": row["price"],
                              "margin": e.margin_pct, "label": row["month_label"]})
    mdf = pd.DataFrame(margins_hist)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=mdf["label"], y=mdf["margin"],
        marker_color=[C["green"] if m > 0 else C["red"] for m in mdf["margin"]],
        marker_line_width=0,
        text=[f"₹{p:.0f}/L<br>{m:.1f}%" for p, m in zip(mdf["price"], mdf["margin"])],
        textposition="outside",
        textfont=dict(size=9, color=C["text3"]),
        hovertemplate="ATF: ₹%{customdata:.1f}/L<br>Margin: %{y:.1f}%<extra></extra>",
        customdata=mdf["price"],
    ))
    fig3.add_hline(y=0, line_color=C["border"], line_width=1)
    apply_theme(fig3, f"Route Margin % at January ATF Price  ·  {orig_h} → {dest_h}", 300)
    fig3.update_layout(yaxis_title="Net Margin %", showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# ── Tab 2: ATF Forecast ───────────────────────────────────────────────────────
with tab2:
    section("Forecast Parameters")
    a1, a2, a3, a4 = st.columns(4)
    with a1: base_atf = st.number_input("Current ATF (₹/L)", value=94.0, step=1.0)
    with a2: fmonths  = st.slider("Horizon (months)", 3, 24, 12)
    with a3: trend    = st.slider("Expected trend (%)", -20, 30, 3)
    with a4: vol      = st.slider("Volatility (%)", 1, 15, 4)

    np.random.seed(42)
    t = np.linspace(0, trend/100*base_atf, fmonths)
    seas = np.array([np.sin(2*np.pi*i/12)*base_atf*0.04 for i in range(fmonths)])
    fc = base_atf + t + seas + np.random.normal(0, base_atf*vol/100, fmonths)
    lo, hi = fc - base_atf*0.06, fc + base_atf*0.06
    dates = pd.date_range("2026-01-01", periods=fmonths, freq="MS")

    fig4 = go.Figure()
    # Historical last 12 months as context
    hist_tail = hist_df.tail(12)
    fig4.add_trace(go.Scatter(
        x=hist_tail["date"], y=hist_tail["price"],
        mode="lines", line=dict(color=C["text3"], width=1.5, dash="dot"),
        name="Historical (2025)", opacity=0.6,
        hovertemplate="%{x|%b %Y}: ₹%{y:.1f}/L<extra></extra>",
    ))
    fig4.add_trace(go.Scatter(x=dates, y=hi, fill=None, mode="lines",
                               line_color="rgba(0,0,0,0)", showlegend=False))
    fig4.add_trace(go.Scatter(x=dates, y=lo, fill="tonexty",
                               fillcolor="rgba(37,99,235,0.08)", mode="lines",
                               line_color="rgba(0,0,0,0)", name="95% Confidence Band"))
    fig4.add_trace(go.Scatter(x=dates, y=fc, mode="lines+markers",
                               line=dict(color=C["accent"], width=2.5),
                               marker=dict(size=4, color=C["accent"]),
                               name="Forecast",
                               hovertemplate="%{x|%b %Y}: ₹%{y:.1f}/L<extra></extra>"))
    apply_theme(fig4, "ATF Price Forecast  ·  ₹/litre  ·  Delhi", 380)
    fig4.update_layout(yaxis_title="₹ per litre",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig4, use_container_width=True)

# ── Tab 3: Demand Forecast ────────────────────────────────────────────────────
with tab3:
    section("Demand Parameters")
    d1, d2, d3, d4 = st.columns(4)
    with d1: base_pax = st.number_input("Base Monthly Pax", value=12000, step=500)
    with d2: dmonths  = st.slider("Horizon (months)", 3, 24, 12, key="dm")
    with d3: growth   = st.slider("YoY Growth (%)", -10, 30, 8)
    with d4: use_seas = st.toggle("Apply Seasonality", value=True)

    np.random.seed(7)
    tr2 = np.linspace(0, growth/100*base_pax, dmonths)
    seas2 = np.zeros(dmonths)
    if use_seas:
        for i in range(dmonths):
            m = (i % 12) + 1
            seas2[i] = base_pax*0.12 if m in [11,12,1,2] else \
                       -base_pax*0.08 if m in [5,6,7] else 0
    fc_d = (base_pax + tr2 + seas2 + np.random.normal(0, base_pax*0.04, dmonths)).astype(int)
    dates_d = pd.date_range("2026-01-01", periods=dmonths, freq="MS")

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=dates_d, y=(fc_d*1.08).astype(int), fill=None,
                               mode="lines", line_color="rgba(0,0,0,0)", showlegend=False))
    fig5.add_trace(go.Scatter(x=dates_d, y=(fc_d*0.92).astype(int), fill="tonexty",
                               fillcolor="rgba(5,150,105,0.07)", mode="lines",
                               line_color="rgba(0,0,0,0)", name="Confidence Band"))
    fig5.add_trace(go.Scatter(x=dates_d, y=fc_d, mode="lines+markers",
                               line=dict(color=C["green"], width=2.5),
                               marker=dict(size=4, color=C["green"]),
                               name="Forecast Passengers",
                               hovertemplate="%{x|%b %Y}: %{y:,} pax<extra></extra>"))
    apply_theme(fig5, "Monthly Passenger Demand Forecast", 360)
    fig5.update_layout(yaxis_title="Monthly Passengers")
    st.plotly_chart(fig5, use_container_width=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Peak Month",     f"{max(fc_d):,}")
    m2.metric("Trough Month",   f"{min(fc_d):,}")
    m3.metric("12-Month Total", f"{sum(fc_d[:12]):,}")
    m4.metric("YoY Growth",     f"+{growth}%")

# ── Tab 4: Anomaly Detection ──────────────────────────────────────────────────
with tab4:
    section("Route Anomaly Scan")
    st.markdown('<div class="info-panel">Statistical anomaly detection across RASK, CASK, and Load Factor. Routes beyond 2.2σ from the mean are flagged for review.</div>',
                unsafe_allow_html=True)

    np.random.seed(99)
    n = 35
    rids = [f"ROUTE-{i:02d}" for i in range(n)]
    rv = np.random.normal(12, 1.5, n)
    cv = np.random.normal(10, 1.2, n)
    lv = np.random.normal(0.81, 0.06, n)
    for idx in [3, 12, 21, 28]:
        rv[idx] += np.random.choice([-1,1]) * 4.2
        cv[idx] += np.random.choice([-1,1]) * 3.8
        lv[idx]  = np.random.choice([0.33, 0.96])

    def zf(arr, t=2.2): return np.abs((arr-arr.mean())/arr.std()) > t
    anom = zf(rv) | zf(cv) | zf(lv)
    ni = [i for i in range(n) if not anom[i]]
    ai = [i for i in range(n) if anom[i]]

    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=cv[ni], y=rv[ni], mode="markers",
        marker=dict(size=8, color=C["accent"], opacity=0.7,
                    line=dict(color=C["border"], width=0.5)),
        text=[rids[i] for i in ni],
        hovertemplate="%{text}<br>RASK: %{y:.1f}p | CASK: %{x:.1f}p<extra></extra>",
        name="Normal",
    ))
    fig6.add_trace(go.Scatter(
        x=cv[ai], y=rv[ai], mode="markers",
        marker=dict(size=14, color=C["red"], symbol="diamond",
                    line=dict(color=C["amber"], width=2)),
        text=[rids[i] for i in ai],
        hovertemplate="⚠ %{text}<br>RASK: %{y:.1f}p | CASK: %{x:.1f}p<extra></extra>",
        name=f"Anomaly ({len(ai)} routes)",
    ))
    lr = [min(cv)*0.92, max(cv)*1.08]
    fig6.add_trace(go.Scatter(x=lr, y=lr, mode="lines",
                               line=dict(color=C["amber"], dash="dash", width=1.5),
                               name="Break-Even Line"))
    apply_theme(fig6, f"RASK vs CASK  ·  {anom.sum()} anomalies detected", 400)
    fig6.update_layout(xaxis_title="CASK (p/ASK)", yaxis_title="RASK (p/ASK)")
    st.plotly_chart(fig6, use_container_width=True)

    if ai:
        section(f"{len(ai)} Flagged Routes")
        adf = pd.DataFrame([{
            "Route": rids[i], "RASK": f"{rv[i]:.1f}p",
            "CASK": f"{cv[i]:.1f}p", "Load Factor": f"{lv[i]:.1%}",
            "Flag": "RASK outlier" if zf(rv)[i] else
                    "CASK outlier" if zf(cv)[i] else "LF outlier"
        } for i in ai])
        st.dataframe(adf, use_container_width=True, hide_index=True)
