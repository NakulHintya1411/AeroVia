"""ML Forecasts — Streamlit page."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · ML Forecasts", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section, apply_theme
from dashboard._shared.styles import COLORS
inject_css()

import plotly.graph_objects as go
import numpy as np, pandas as pd
from config.constants import INDIAN_AIRPORTS, AIRCRAFT_TYPES
from economics.engine import RouteInputs, compute_route_economics

with st.sidebar:
    sidebar_logo()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>', unsafe_allow_html=True)

page_header("Predictive Analytics", "ML Forecasts",
            "ATF fuel price forecasting, route demand prediction, and statistical anomaly detection.")

C = COLORS
tab1, tab2, tab3 = st.tabs(["ATF Price Forecast", "Demand Forecast", "Anomaly Detection"])

with tab1:
    section("Forecast Parameters")
    a1,a2,a3,a4 = st.columns(4)
    with a1: base_atf = st.number_input("Current ATF (₹/L)", value=95.0, step=1.0)
    with a2: fmonths  = st.slider("Horizon (months)", 3, 24, 12)
    with a3: trend    = st.slider("Expected trend (%)", -20, 30, 5)
    with a4: vol      = st.slider("Volatility (%)", 1, 15, 4)

    np.random.seed(42)
    t = np.linspace(0, trend/100*base_atf, fmonths)
    seas = np.array([np.sin(2*np.pi*i/12)*base_atf*0.05 for i in range(fmonths)])
    fc = base_atf + t + seas + np.random.normal(0, base_atf*vol/100, fmonths)
    lo, hi = fc - base_atf*0.06, fc + base_atf*0.06
    dates = pd.date_range("2024-01-01", periods=fmonths, freq="MS")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=hi, fill=None, mode="lines",
                              line_color="rgba(0,0,0,0)", showlegend=False))
    fig.add_trace(go.Scatter(x=dates, y=lo, fill="tonexty",
                              fillcolor="rgba(37,99,235,0.08)", mode="lines",
                              line_color="rgba(0,0,0,0)", name="Confidence Band"))
    fig.add_trace(go.Scatter(x=dates, y=fc, mode="lines+markers",
                              line=dict(color=C["accent"], width=2.5),
                              marker=dict(size=4, color=C["accent"]), name="Forecast",
                              hovertemplate="%{x|%b %Y}: ₹%{y:.1f}/L<extra></extra>"))
    fig.add_hline(y=base_atf, line_dash="dash", line_color=C["text3"], line_width=1,
                  annotation_text=f"Current ₹{base_atf:.0f}/L",
                  annotation_font=dict(size=11, color=C["text3"]))
    apply_theme(fig, "ATF Price Forecast (₹/litre)", 360)
    fig.update_layout(yaxis_title="₹ per litre")
    st.plotly_chart(fig, use_container_width=True)

    section("ATF Impact on Route Margin")
    ap = {f"{k} — {v['city']}": k for k, v in INDIAN_AIRPORTS.items()}
    ri1,ri2,ri3 = st.columns(3)
    with ri1: orig = ap[st.selectbox("Origin", list(ap.keys()), index=0, key="atf_o")]
    with ri2:
        dopts = {k:v for k,v in ap.items() if v!=orig}
        dest = dopts[st.selectbox("Destination", list(dopts.keys()), index=4, key="atf_d")]
    with ri3: rac = st.selectbox("Aircraft", list(AIRCRAFT_TYPES.keys()), key="atf_ac")

    atf_vals = list(range(70, 131, 5))
    margins = [compute_route_economics(RouteInputs(orig,dest,"6E",rac,3,0.82,
               atf_price_inr_per_litre=float(av))).margin_pct for av in atf_vals]
    fig2 = go.Figure(go.Bar(
        x=[f"₹{v}" for v in atf_vals], y=margins,
        marker_color=[C["green"] if m>0 else C["red"] for m in margins],
        marker_line_width=0,
        text=[f"{m:.1f}%" for m in margins], textposition="outside",
        textfont=dict(size=10, color=C["text3"]),
    ))
    fig2.add_hline(y=0, line_color=C["border"], line_width=1)
    apply_theme(fig2, f"Margin % vs ATF Price  —  {orig} → {dest}", 300)
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    section("Demand Parameters")
    d1,d2,d3,d4 = st.columns(4)
    with d1: base_pax = st.number_input("Base Monthly Pax", value=12000, step=500)
    with d2: dmonths  = st.slider("Horizon (months)", 3, 24, 12, key="dm")
    with d3: growth   = st.slider("YoY Growth (%)", -10, 30, 8)
    with d4: use_seas = st.toggle("Apply Seasonality", value=True)

    np.random.seed(7)
    tr2 = np.linspace(0, growth/100*base_pax, dmonths)
    seas2 = np.zeros(dmonths)
    if use_seas:
        for i in range(dmonths):
            m = (i%12)+1
            seas2[i] = base_pax*0.12 if m in [11,12,1,2] else -base_pax*0.08 if m in [5,6,7] else 0
    fc_d = (base_pax + tr2 + seas2 + np.random.normal(0, base_pax*0.04, dmonths)).astype(int)
    dates_d = pd.date_range("2024-01-01", periods=dmonths, freq="MS")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=dates_d, y=(fc_d*1.08).astype(int), fill=None, mode="lines",
                               line_color="rgba(0,0,0,0)", showlegend=False))
    fig3.add_trace(go.Scatter(x=dates_d, y=(fc_d*0.92).astype(int), fill="tonexty",
                               fillcolor="rgba(5,150,105,0.07)", mode="lines",
                               line_color="rgba(0,0,0,0)", name="Confidence Band"))
    fig3.add_trace(go.Scatter(x=dates_d, y=fc_d, mode="lines+markers",
                               line=dict(color=C["green"], width=2.5),
                               marker=dict(size=4, color=C["green"]), name="Forecast",
                               hovertemplate="%{x|%b %Y}: %{y:,} pax<extra></extra>"))
    apply_theme(fig3, "Monthly Demand Forecast", 360)
    fig3.update_layout(yaxis_title="Monthly Passengers")
    st.plotly_chart(fig3, use_container_width=True)

    m1,m2,m3 = st.columns(3)
    m1.metric("Peak Month",    f"{max(fc_d):,}")
    m2.metric("Trough Month",  f"{min(fc_d):,}")
    m3.metric("12-Month Total",f"{sum(fc_d[:12]):,}")

with tab3:
    section("Route Anomaly Scan")
    st.markdown('<div class="info-panel">Z-score anomaly detection across RASK, CASK, and Load Factor. Routes beyond 2.2σ are flagged for review.</div>', unsafe_allow_html=True)

    np.random.seed(99)
    n = 35
    rids = [f"ROUTE-{i:02d}" for i in range(n)]
    rv = np.random.normal(12,1.5,n); cv = np.random.normal(10,1.2,n); lv = np.random.normal(0.81,0.06,n)
    for idx in [3,12,21,28]:
        rv[idx] += np.random.choice([-1,1])*4.2
        cv[idx] += np.random.choice([-1,1])*3.8
        lv[idx] = np.random.choice([0.33,0.96])

    def zf(arr, t=2.2): return np.abs((arr-arr.mean())/arr.std()) > t
    anom = zf(rv)|zf(cv)|zf(lv)
    ni = [i for i in range(n) if not anom[i]]
    ai = [i for i in range(n) if anom[i]]

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=cv[ni], y=rv[ni], mode="markers",
                               marker=dict(size=8, color=C["accent"], opacity=0.7,
                                           line=dict(color=C["border"], width=0.5)),
                               text=[rids[i] for i in ni],
                               hovertemplate="%{text}<br>RASK: %{y:.1f}p | CASK: %{x:.1f}p<extra></extra>",
                               name="Normal"))
    fig4.add_trace(go.Scatter(x=cv[ai], y=rv[ai], mode="markers",
                               marker=dict(size=14, color=C["red"], symbol="diamond",
                                           line=dict(color=C["amber"], width=2)),
                               text=[rids[i] for i in ai],
                               hovertemplate="⚠ %{text}<br>RASK: %{y:.1f}p | CASK: %{x:.1f}p<extra></extra>",
                               name=f"Anomaly ({len(ai)})"))
    lr = [min(cv)*0.92, max(cv)*1.08]
    fig4.add_trace(go.Scatter(x=lr, y=lr, mode="lines",
                               line=dict(color=C["amber"], dash="dash", width=1.5), name="Break-Even"))
    apply_theme(fig4, f"RASK vs CASK Scatter  —  {anom.sum()} anomalies detected", 400)
    fig4.update_layout(xaxis_title="CASK (p/ASK)", yaxis_title="RASK (p/ASK)")
    st.plotly_chart(fig4, use_container_width=True)

    if ai:
        section(f"{len(ai)} Flagged Routes")
        adf = pd.DataFrame([{"Route":rids[i],"RASK":f"{rv[i]:.1f}p","CASK":f"{cv[i]:.1f}p",
                               "Load Factor":f"{lv[i]:.1%}",
                               "Flag":"RASK outlier" if zf(rv)[i] else "CASK outlier" if zf(cv)[i] else "LF outlier"}
                              for i in ai])
        st.dataframe(adf, use_container_width=True, hide_index=True)
