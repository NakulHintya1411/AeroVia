"""ML Forecasts — ATF price forecast + demand prediction (Prophet-free fallback)."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from config.constants import INDIAN_AIRPORTS, AIRCRAFT_TYPES


def _simple_atf_forecast(base_price: float, months: int, trend_pct: float, volatility: float):
    """Simple trend + seasonal + noise ATF forecast (no Prophet dependency)."""
    np.random.seed(42)
    periods = months
    trend = np.linspace(0, trend_pct / 100 * base_price, periods)
    seasonal = np.array([np.sin(2 * np.pi * i / 12) * base_price * 0.05 for i in range(periods)])
    noise = np.random.normal(0, base_price * volatility / 100, periods)
    forecast = base_price + trend + seasonal + noise
    lower = forecast - base_price * 0.06
    upper = forecast + base_price * 0.06
    months_idx = pd.date_range(start="2024-01-01", periods=periods, freq="MS")
    return months_idx, forecast, lower, upper


def _demand_forecast(base_pax: int, months: int, growth_pct: float, seasonality: bool):
    np.random.seed(7)
    trend = np.linspace(0, growth_pct / 100 * base_pax, months)
    seasonal = np.zeros(months)
    if seasonality:
        for i in range(months):
            m = (i % 12) + 1
            if m in [11, 12, 1, 2]:
                seasonal[i] = base_pax * 0.12
            elif m in [5, 6, 7]:
                seasonal[i] = -base_pax * 0.08
    noise = np.random.normal(0, base_pax * 0.04, months)
    forecast = base_pax + trend + seasonal + noise
    lower = forecast * 0.92
    upper = forecast * 1.08
    months_idx = pd.date_range(start="2024-01-01", periods=months, freq="MS")
    return months_idx, forecast.astype(int), lower.astype(int), upper.astype(int)


def render():
    st.title("🤖 ML Forecasts")
    st.caption("ATF fuel price forecasting and route demand prediction.")

    tab1, tab2, tab3 = st.tabs(["⛽ ATF Price Forecast", "📈 Demand Forecast", "🔍 Anomaly Detection"])

    # ── Tab 1: ATF Forecast ───────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">ATF Price Forecast</div>', unsafe_allow_html=True)
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            base_atf = st.number_input("Current ATF Price (₹/L)", value=95.0, step=1.0)
        with a2:
            forecast_months = st.slider("Forecast Horizon (months)", 3, 24, 12)
        with a3:
            trend_pct = st.slider("Expected Trend (%)", -20, 30, 5)
        with a4:
            volatility = st.slider("Volatility (%)", 1, 15, 4)

        months_idx, atf_fc, atf_lo, atf_hi = _simple_atf_forecast(base_atf, forecast_months, trend_pct, volatility)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months_idx, y=atf_hi,
            fill=None, mode="lines", line_color="rgba(59,130,246,0)", showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=months_idx, y=atf_lo,
            fill="tonexty", fillcolor="rgba(59,130,246,0.12)",
            mode="lines", line_color="rgba(59,130,246,0)", name="Confidence Band"
        ))
        fig.add_trace(go.Scatter(
            x=months_idx, y=atf_fc,
            mode="lines+markers", line=dict(color="#3b82f6", width=2.5),
            marker=dict(size=5), name="ATF Forecast",
        ))
        fig.add_hline(y=base_atf, line_dash="dot", line_color="#475569",
                      annotation_text=f"Current ₹{base_atf:.0f}/L", annotation_font_color="#94a3b8")
        fig.update_layout(
            plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
            font_color="#c8d6f0", font_family="DM Sans",
            height=360, margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(gridcolor="#1e2d4a"),
            yaxis=dict(title="ATF Price (₹/L)", gridcolor="#1e2d4a"),
            legend=dict(bgcolor="#0d1426", bordercolor="#1e3058"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ATF Impact on route
        st.markdown('<div class="section-header">ATF Impact on Route Economics</div>', unsafe_allow_html=True)
        from economics.engine import RouteInputs, compute_route_economics
        airport_options = {f"{k} — {v['city']}": k for k, v in INDIAN_AIRPORTS.items()}
        ai1, ai2, ai3 = st.columns(3)
        with ai1:
            orig = airport_options[st.selectbox("Origin", list(airport_options.keys()), index=0, key="atf_orig")]
        with ai2:
            dest_opts = {k: v for k, v in airport_options.items() if v != orig}
            dest = dest_opts[st.selectbox("Destination", list(dest_opts.keys()), index=4, key="atf_dest")]
        with ai3:
            ac = st.selectbox("Aircraft", list(AIRCRAFT_TYPES.keys()), key="atf_ac")

        atf_vals = list(range(70, 131, 5))
        margins = []
        for av in atf_vals:
            inp = RouteInputs(origin=orig, destination=dest, airline_code="6E",
                              aircraft_type=ac, daily_frequency=3, load_factor=0.82,
                              atf_price_inr_per_litre=float(av))
            margins.append(compute_route_economics(inp).margin_pct)

        fig2 = go.Figure()
        colors_m = ["#34d399" if m > 0 else "#f87171" for m in margins]
        fig2.add_trace(go.Bar(x=[f"₹{v}" for v in atf_vals], y=margins,
                              marker_color=colors_m,
                              text=[f"{m:.1f}%" for m in margins],
                              textposition="outside"))
        fig2.add_hline(y=0, line_color="#475569")
        fig2.update_layout(
            title=f"Margin % vs ATF Price — {orig} → {dest}",
            plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
            font_color="#c8d6f0", font_family="DM Sans",
            height=300, margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(title="Margin %", gridcolor="#1e2d4a"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 2: Demand Forecast ─────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Route Demand Forecast</div>', unsafe_allow_html=True)
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            base_pax = st.number_input("Base Monthly Passengers", value=12000, step=500)
        with b2:
            d_months = st.slider("Forecast Months", 3, 24, 12, key="d_months")
        with b3:
            growth = st.slider("YoY Growth (%)", -10, 30, 8)
        with b4:
            use_seasonal = st.toggle("Apply Seasonality", value=True)

        months_idx, pax_fc, pax_lo, pax_hi = _demand_forecast(base_pax, d_months, growth, use_seasonal)

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=months_idx, y=pax_hi, fill=None, mode="lines",
                                  line_color="rgba(52,211,153,0)", showlegend=False))
        fig3.add_trace(go.Scatter(x=months_idx, y=pax_lo, fill="tonexty",
                                  fillcolor="rgba(52,211,153,0.1)", mode="lines",
                                  line_color="rgba(52,211,153,0)", name="Confidence Band"))
        fig3.add_trace(go.Scatter(x=months_idx, y=pax_fc, mode="lines+markers",
                                  line=dict(color="#34d399", width=2.5),
                                  marker=dict(size=5), name="Forecast Passengers"))
        fig3.update_layout(
            plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
            font_color="#c8d6f0", font_family="DM Sans",
            height=360, margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(gridcolor="#1e2d4a"),
            yaxis=dict(title="Monthly Passengers", gridcolor="#1e2d4a"),
            legend=dict(bgcolor="#0d1426", bordercolor="#1e3058"),
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Summary stats
        s1, s2, s3 = st.columns(3)
        s1.metric("Peak Month Forecast", f"{max(pax_fc):,}")
        s2.metric("Trough Month Forecast", f"{min(pax_fc):,}")
        s3.metric("12-Month Total", f"{sum(pax_fc[:12]):,}")

    # ── Tab 3: Anomaly Detection ───────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Route Anomaly Detection</div>', unsafe_allow_html=True)
        st.caption("Detects routes with unusual RASK, CASK or LF patterns.")

        np.random.seed(99)
        n = 30
        route_ids = [f"Route-{i:02d}" for i in range(n)]
        rask_vals = np.random.normal(12, 1.5, n)
        cask_vals = np.random.normal(10, 1.2, n)
        lf_vals_an = np.random.normal(0.81, 0.06, n)

        # Inject anomalies
        for idx in [3, 12, 21]:
            rask_vals[idx] += np.random.choice([-1, 1]) * 4
            cask_vals[idx] += np.random.choice([-1, 1]) * 3.5
            lf_vals_an[idx] = np.random.choice([0.35, 0.97])

        # Simple z-score anomaly flag
        def z_flag(arr, threshold=2.2):
            z = np.abs((arr - arr.mean()) / arr.std())
            return z > threshold

        rask_anom = z_flag(rask_vals)
        cask_anom = z_flag(cask_vals)
        lf_anom = z_flag(lf_vals_an)
        is_anomaly = rask_anom | cask_anom | lf_anom

        colors_anom = ["#f87171" if a else "#3b82f6" for a in is_anomaly]
        sizes_anom = [14 if a else 7 for a in is_anomaly]

        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=cask_vals, y=rask_vals,
            mode="markers",
            marker=dict(size=sizes_anom, color=colors_anom,
                        line=dict(width=[2 if a else 0 for a in is_anomaly], color="#fbbf24")),
            text=[f"{r} {'⚠ ANOMALY' if a else ''}" for r, a in zip(route_ids, is_anomaly)],
            hoverinfo="text",
        ))
        fig4.add_trace(go.Scatter(
            x=[min(cask_vals)*0.95, max(cask_vals)*1.05],
            y=[min(cask_vals)*0.95, max(cask_vals)*1.05],
            mode="lines", line=dict(color="#fbbf24", dash="dash"),
            name="Break-Even Line"
        ))
        fig4.update_layout(
            title=f"{is_anomaly.sum()} anomalous routes detected (red = outlier)",
            plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
            font_color="#c8d6f0", font_family="DM Sans",
            height=400, margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(title="CASK", gridcolor="#1e2d4a"),
            yaxis=dict(title="RASK", gridcolor="#1e2d4a"),
            showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)

        anom_routes = [(route_ids[i], f"{rask_vals[i]:.1f}", f"{cask_vals[i]:.1f}", f"{lf_vals_an[i]:.1%}")
                       for i in range(n) if is_anomaly[i]]
        if anom_routes:
            anom_df = pd.DataFrame(anom_routes, columns=["Route", "RASK", "CASK", "Load Factor"])
            st.dataframe(anom_df, use_container_width=True, hide_index=True)
