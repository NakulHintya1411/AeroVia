"""Route Builder — user picks route, aircraft, costs; sees live economics."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from config.constants import INDIAN_AIRPORTS, AIRLINES, AIRCRAFT_TYPES, DEFAULT_COST_ASSUMPTIONS
from economics.engine import RouteInputs, compute_route_economics
from economics.scenario_store import save_scenario


def render():
    st.title("✈ Route Builder")
    st.caption("Configure any Indian domestic route and get instant profitability analysis.")

    # ── Route Selection ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Route Configuration</div>', unsafe_allow_html=True)

    airport_options = {f"{k} — {v['city']}": k for k, v in INDIAN_AIRPORTS.items()}

    col1, col2, col3 = st.columns(3)
    with col1:
        origin_label = st.selectbox("Origin Airport", list(airport_options.keys()), index=0)
        origin = airport_options[origin_label]
    with col2:
        dest_options = {k: v for k, v in airport_options.items() if v != origin}
        destination_label = st.selectbox("Destination Airport", list(dest_options.keys()), index=4)
        destination = dest_options[destination_label]
    with col3:
        airline_options = {f"{k} — {v['name']}": k for k, v in AIRLINES.items()}
        airline_label = st.selectbox("Operating Airline", list(airline_options.keys()))
        airline = airline_options[airline_label]

    col4, col5, col6 = st.columns(3)
    with col4:
        aircraft_type = st.selectbox("Aircraft Type", list(AIRCRAFT_TYPES.keys()))
    with col5:
        daily_frequency = st.number_input("Daily Frequency (flights/day)", min_value=1, max_value=12, value=3)
    with col6:
        load_factor = st.slider("Load Factor (%)", min_value=40, max_value=100, value=82) / 100

    # ── Cost Assumptions ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Cost Assumptions</div>', unsafe_allow_html=True)
    st.caption("Override defaults or leave as-is to use industry benchmarks.")

    with st.expander("⚙ Customize Cost Inputs", expanded=False):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            atf = st.number_input("ATF Price (₹/litre)", value=DEFAULT_COST_ASSUMPTIONS["atf_price_inr_per_litre"], step=1.0, format="%.1f")
            crew_pct = st.number_input("Crew Cost (% of revenue)", value=DEFAULT_COST_ASSUMPTIONS["crew_cost_pct_of_revenue"] * 100, step=0.5, format="%.1f") / 100
        with cc2:
            maint = st.number_input("Maintenance Cost (₹/flight hr)", value=float(DEFAULT_COST_ASSUMPTIONS["maintenance_cost_per_flight_hour"]), step=500.0)
            airport_ch = st.number_input("Airport Charges (₹/sector)", value=float(DEFAULT_COST_ASSUMPTIONS["airport_charges_per_sector"]), step=500.0)
        with cc3:
            overhead_pct = st.number_input("Overhead (% of revenue)", value=DEFAULT_COST_ASSUMPTIONS["overhead_pct_of_revenue"] * 100, step=0.5, format="%.1f") / 100
            yield_inr = st.number_input("Avg Yield (₹/RPK)", value=DEFAULT_COST_ASSUMPTIONS["avg_yield_inr_per_km"], step=0.1, format="%.2f")

    # ── Compute ───────────────────────────────────────────────────────────────
    inputs = RouteInputs(
        origin=origin,
        destination=destination,
        airline_code=airline,
        aircraft_type=aircraft_type,
        daily_frequency=daily_frequency,
        load_factor=load_factor,
        atf_price_inr_per_litre=atf if 'atf' in dir() else None,
        crew_cost_pct=crew_pct if 'crew_pct' in dir() else None,
        maintenance_cost_per_fh=maint if 'maint' in dir() else None,
        airport_charges_per_sector=airport_ch if 'airport_ch' in dir() else None,
        overhead_pct=overhead_pct if 'overhead_pct' in dir() else None,
        yield_inr_per_km=yield_inr if 'yield_inr' in dir() else None,
    )
    econ = compute_route_economics(inputs)

    # ── Route badge ───────────────────────────────────────────────────────────
    badge_class = "badge-profit" if econ.margin_pct > 2 else "badge-loss" if econ.margin_pct < 0 else "badge-break"
    badge_text = f"{'PROFITABLE' if econ.margin_pct > 2 else 'LOSS-MAKING' if econ.margin_pct < 0 else 'BREAKEVEN'}"
    st.markdown(f"""
    <div style="margin: 16px 0; display:flex; align-items:center; gap:16px">
        <span class="route-tag">{origin} → {destination}</span>
        <span style="color:#5b7fa6">|</span>
        <span style="color:#93b4d8; font-size:13px">{econ.distance_km:,.0f} km · {econ.flight_time_hr:.1f}h · {AIRCRAFT_TYPES[aircraft_type]['seats']} seats</span>
        <span class="profit-badge {badge_class}">{badge_text}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Metrics ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Key Metrics (Daily)</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)

    def kpi(col, label, value, delta=None, delta_pos=True):
        delta_html = ""
        if delta is not None:
            cls = "delta-pos" if delta_pos else "delta-neg"
            arrow = "▲" if delta_pos else "▼"
            delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>'
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>""", unsafe_allow_html=True)

    kpi(k1, "RASK (paise/ASK)", f"{econ.rask:.1f}p")
    kpi(k2, "CASK (paise/ASK)", f"{econ.cask:.1f}p")
    kpi(k3, "Margin", f"{econ.margin_pct:.1f}%", delta_pos=econ.margin_pct > 0)
    kpi(k4, "BELF", f"{econ.belf*100:.1f}%")
    kpi(k5, "LF Cushion", f"{econ.lf_cushion*100:+.1f}pp", delta_pos=econ.lf_cushion > 0)

    # ── Revenue vs Cost breakdown ─────────────────────────────────────────────
    st.markdown('<div class="section-header">Cost & Revenue Breakdown</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)

    with ch1:
        # Waterfall cost chart
        cost_items = {
            "Fuel": econ.fuel_cost_inr,
            "Crew": econ.crew_cost_inr,
            "Maintenance": econ.maintenance_cost_inr,
            "Airport": econ.airport_cost_inr,
            "Overhead": econ.overhead_cost_inr,
        }
        colors = ["#f87171", "#fb923c", "#fbbf24", "#a78bfa", "#60a5fa"]
        fig = go.Figure(go.Bar(
            x=list(cost_items.keys()),
            y=[v/1e5 for v in cost_items.values()],
            marker_color=colors,
            text=[f"₹{v/1e5:.1f}L" for v in cost_items.values()],
            textposition="outside",
        ))
        fig.update_layout(
            title="Daily Cost Breakdown (₹ Lakhs)",
            plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
            font_color="#c8d6f0", font_family="DM Sans",
            showlegend=False, height=320,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(gridcolor="#1e2d4a"),
            xaxis=dict(gridcolor="#1e2d4a"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        # Revenue vs Cost gauge-style
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name="Revenue", x=["Daily P&L"],
            y=[econ.total_revenue_inr / 1e5],
            marker_color="#34d399",
            text=f"₹{econ.total_revenue_inr/1e5:.1f}L",
            textposition="outside",
        ))
        fig2.add_trace(go.Bar(
            name="Total Cost", x=["Daily P&L"],
            y=[econ.total_cost_inr / 1e5],
            marker_color="#f87171",
            text=f"₹{econ.total_cost_inr/1e5:.1f}L",
            textposition="outside",
        ))
        profit_color = "#34d399" if econ.profit_inr >= 0 else "#f87171"
        fig2.add_annotation(
            text=f"Profit: ₹{econ.profit_inr/1e5:.1f}L/day",
            x=0, y=max(econ.total_revenue_inr, econ.total_cost_inr) / 1e5 * 1.15,
            font=dict(size=14, color=profit_color, family="Space Mono"),
            showarrow=False,
        )
        fig2.update_layout(
            title="Revenue vs Total Cost",
            barmode="group",
            plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
            font_color="#c8d6f0", font_family="DM Sans",
            height=320,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(gridcolor="#1e2d4a"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── BELF vs LF visual ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Break-Even Load Factor Analysis</div>', unsafe_allow_html=True)
    lf_vals = [i/100 for i in range(40, 101)]
    profit_vals = []
    for lf in lf_vals:
        test_inp = RouteInputs(
            origin=origin, destination=destination, airline_code=airline,
            aircraft_type=aircraft_type, daily_frequency=daily_frequency, load_factor=lf,
            atf_price_inr_per_litre=inputs.atf_price_inr_per_litre,
            crew_cost_pct=inputs.crew_cost_pct,
            maintenance_cost_per_fh=inputs.maintenance_cost_per_fh,
            airport_charges_per_sector=inputs.airport_charges_per_sector,
            overhead_pct=inputs.overhead_pct,
            yield_inr_per_km=inputs.yield_inr_per_km,
        )
        profit_vals.append(compute_route_economics(test_inp).profit_inr / 1e5)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=[lf * 100 for lf in lf_vals], y=profit_vals,
        mode="lines", line=dict(color="#3b82f6", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.1)",
        name="Daily Profit (₹L)",
    ))
    fig3.add_vline(x=econ.belf * 100, line_dash="dash", line_color="#fbbf24",
                   annotation_text=f"BELF {econ.belf*100:.1f}%", annotation_font_color="#fbbf24")
    fig3.add_vline(x=load_factor * 100, line_dash="dot", line_color="#34d399",
                   annotation_text=f"Current LF {load_factor*100:.0f}%", annotation_font_color="#34d399")
    fig3.add_hline(y=0, line_color="#475569")
    fig3.update_layout(
        plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
        font_color="#c8d6f0", font_family="DM Sans",
        height=280, showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(title="Load Factor (%)", gridcolor="#1e2d4a"),
        yaxis=dict(title="Daily Profit (₹ Lakhs)", gridcolor="#1e2d4a"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Save Scenario ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Save This Scenario</div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        scenario_name = st.text_input("Scenario name", value=f"{origin}-{destination} | {airline} | LF {load_factor*100:.0f}%")
    with sc2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Scenario"):
            save_scenario(scenario_name, vars(inputs), econ.to_dict())
            st.success(f"Saved: **{scenario_name}**")
