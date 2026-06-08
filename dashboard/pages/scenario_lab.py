"""Scenario Lab — live what-if sliders + saved scenario comparison."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from config.constants import INDIAN_AIRPORTS, AIRLINES, AIRCRAFT_TYPES, DEFAULT_COST_ASSUMPTIONS
from economics.engine import RouteInputs, compute_route_economics, sensitivity_grid
from economics.scenario_store import list_scenarios, get_scenario, compare_scenarios, delete_scenario


def render():
    st.title("⚗ Scenario Lab")
    st.caption("Run live what-if analysis and compare saved scenarios side-by-side.")

    tab1, tab2, tab3 = st.tabs(["🎛 Live What-If", "📊 Compare Scenarios", "🌡 Sensitivity Heatmap"])

    # ── Tab 1: Live What-If ───────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">Base Route</div>', unsafe_allow_html=True)
        airport_options = {f"{k} — {v['city']}": k for k, v in INDIAN_AIRPORTS.items()}

        bc1, bc2, bc3, bc4 = st.columns(4)
        with bc1:
            origin_label = st.selectbox("Origin", list(airport_options.keys()), index=0, key="sc_orig")
            origin = airport_options[origin_label]
        with bc2:
            dest_opts = {k: v for k, v in airport_options.items() if v != origin}
            dest_label = st.selectbox("Destination", list(dest_opts.keys()), index=4, key="sc_dest")
            destination = dest_opts[dest_label]
        with bc3:
            ac_type = st.selectbox("Aircraft", list(AIRCRAFT_TYPES.keys()), key="sc_ac")
        with bc4:
            freq = st.number_input("Flights/day", 1, 12, 3, key="sc_freq")

        st.markdown('<div class="section-header">What-If Sliders</div>', unsafe_allow_html=True)
        st.caption("Adjust any parameter below — all metrics update instantly.")

        s1, s2, s3 = st.columns(3)
        with s1:
            lf_what = st.slider("Load Factor (%)", 40, 100, 82, key="sc_lf") / 100
            atf_what = st.slider("ATF Price (₹/L)", 60, 140, 95, key="sc_atf", step=1)
        with s2:
            yield_what = st.slider("Avg Yield (₹/RPK)", 2.0, 8.0, 4.2, step=0.1, key="sc_yield")
            crew_what = st.slider("Crew Cost (% rev)", 5, 20, 12, key="sc_crew") / 100
        with s3:
            freq_what = st.slider("Frequency (flights/day)", 1, 12, freq, key="sc_freq2")
            overhead_what = st.slider("Overhead (% rev)", 3, 15, 8, key="sc_oh") / 100

        base_inp = RouteInputs(
            origin=origin, destination=destination,
            airline_code="6E", aircraft_type=ac_type, daily_frequency=freq,
            load_factor=0.82, atf_price_inr_per_litre=95,
            yield_inr_per_km=4.2, crew_cost_pct=0.12, overhead_pct=0.08,
        )
        what_inp = RouteInputs(
            origin=origin, destination=destination,
            airline_code="6E", aircraft_type=ac_type, daily_frequency=freq_what,
            load_factor=lf_what, atf_price_inr_per_litre=float(atf_what),
            yield_inr_per_km=yield_what, crew_cost_pct=crew_what, overhead_pct=overhead_what,
        )
        base_econ = compute_route_economics(base_inp)
        what_econ = compute_route_economics(what_inp)

        # Delta comparison cards
        st.markdown('<div class="section-header">Impact vs Base Case</div>', unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)

        def delta_card(col, label, base_val, what_val, fmt=".1f", suffix=""):
            delta = what_val - base_val
            pos = delta >= 0
            col.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{what_val:{fmt}}{suffix}</div>
                <div class="metric-delta {'delta-pos' if pos else 'delta-neg'}">
                    {'▲' if pos else '▼'} {abs(delta):{fmt}}{suffix} vs base
                </div>
            </div>""", unsafe_allow_html=True)

        delta_card(d1, "Margin %", base_econ.margin_pct, what_econ.margin_pct, ".1f", "%")
        delta_card(d2, "RASK (paise)", base_econ.rask, what_econ.rask, ".1f", "p")
        delta_card(d3, "CASK (paise)", base_econ.cask, what_econ.cask, ".1f", "p", )
        delta_card(d4, "Daily Profit (₹L)", base_econ.profit_inr/1e5, what_econ.profit_inr/1e5, ".1f", "L")

        # Visual comparison
        metrics = ["RASK", "CASK", "Margin %", "BELF %"]
        base_vals = [base_econ.rask, base_econ.cask, base_econ.margin_pct, base_econ.belf*100]
        what_vals = [what_econ.rask, what_econ.cask, what_econ.margin_pct, what_econ.belf*100]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Base Case", x=metrics, y=base_vals, marker_color="#475569"))
        fig.add_trace(go.Bar(name="What-If", x=metrics, y=what_vals, marker_color="#3b82f6"))
        fig.update_layout(
            barmode="group",
            plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
            font_color="#c8d6f0", font_family="DM Sans",
            height=300, margin=dict(l=10, r=10, t=20, b=10),
            yaxis=dict(gridcolor="#1e2d4a"),
            legend=dict(bgcolor="#0d1426", bordercolor="#1e3058"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Tab 2: Compare Saved Scenarios ────────────────────────────────────────
    with tab2:
        saved = list_scenarios()
        if not saved:
            st.info("No saved scenarios yet. Build and save routes in the **Route Builder** tab.")
        else:
            selected = st.multiselect("Select scenarios to compare", saved, default=saved[:min(3, len(saved))])
            if selected:
                scenarios = compare_scenarios(selected)
                # Build comparison table
                rows = []
                for sc in scenarios:
                    e = sc["economics"]
                    rows.append({
                        "Scenario": sc["name"],
                        "Route": f"{e['origin']} → {e['destination']}",
                        "Aircraft": e["aircraft_type"],
                        "LF %": f"{e['load_factor']*100:.0f}%",
                        "RASK (p)": f"{e['rask']:.1f}",
                        "CASK (p)": f"{e['cask']:.1f}",
                        "Margin %": f"{e['margin_pct']:.1f}%",
                        "BELF %": f"{e['belf']*100:.1f}%",
                        "Daily Profit": f"₹{e['profit_inr']/1e5:.1f}L",
                    })
                import pandas as pd
                df = pd.DataFrame(rows).set_index("Scenario")
                st.dataframe(df, use_container_width=True)

                # Chart comparison
                fig = go.Figure()
                for sc in scenarios:
                    e = sc["economics"]
                    fig.add_trace(go.Scattergl(
                        x=[e["cask"]], y=[e["rask"]],
                        mode="markers+text",
                        marker=dict(size=16, color="#3b82f6"),
                        text=[sc["name"][:20]],
                        textposition="top center",
                        name=sc["name"][:20],
                    ))
                # break-even line
                all_cask = [sc["economics"]["cask"] for sc in scenarios]
                line_x = [min(all_cask)*0.9, max(all_cask)*1.1]
                fig.add_trace(go.Scatter(
                    x=line_x, y=line_x, mode="lines",
                    line=dict(color="#fbbf24", dash="dash"),
                    name="Break-Even (RASK=CASK)",
                ))
                fig.update_layout(
                    title="RASK vs CASK (above diagonal = profitable)",
                    plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
                    font_color="#c8d6f0", height=350,
                    margin=dict(l=10, r=10, t=40, b=10),
                    xaxis=dict(title="CASK (paise/ASK)", gridcolor="#1e2d4a"),
                    yaxis=dict(title="RASK (paise/ASK)", gridcolor="#1e2d4a"),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Delete
                to_delete = st.selectbox("Delete a scenario", ["—"] + saved)
                if to_delete != "—" and st.button("🗑 Delete"):
                    delete_scenario(to_delete)
                    st.rerun()

                # Export
                import io
                csv_buf = io.StringIO()
                df.to_csv(csv_buf)
                st.download_button("📥 Export Comparison CSV", csv_buf.getvalue(), "aerovia_scenarios.csv", "text/csv")

    # ── Tab 3: Sensitivity Heatmap ────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Sensitivity Heatmap</div>', unsafe_allow_html=True)
        st.caption("See how margin changes across two parameters simultaneously.")

        ha1, ha2, ha3 = st.columns(3)
        with ha1:
            h_orig_label = st.selectbox("Route Origin", list(airport_options.keys()), index=0, key="h_orig")
            h_orig = airport_options[h_orig_label]
        with ha2:
            h_dest_opts = {k: v for k, v in airport_options.items() if v != h_orig}
            h_dest_label = st.selectbox("Route Destination", list(h_dest_opts.keys()), index=4, key="h_dest")
            h_dest = h_dest_opts[h_dest_label]
        with ha3:
            h_ac = st.selectbox("Aircraft", list(AIRCRAFT_TYPES.keys()), key="h_ac")

        lf_range = [lf/100 for lf in range(55, 96, 5)]
        atf_range = list(range(75, 126, 5))

        # Compute grid
        margins = []
        for atf_val in atf_range:
            row = []
            for lf_val in lf_range:
                inp = RouteInputs(
                    origin=h_orig, destination=h_dest, airline_code="6E",
                    aircraft_type=h_ac, daily_frequency=3, load_factor=lf_val,
                    atf_price_inr_per_litre=float(atf_val),
                )
                row.append(compute_route_economics(inp).margin_pct)
            margins.append(row)

        fig = go.Figure(go.Heatmap(
            z=margins,
            x=[f"{lf*100:.0f}%" for lf in lf_range],
            y=[f"₹{a}/L" for a in atf_range],
            colorscale=[[0, "#7f1d1d"], [0.4, "#fbbf24"], [0.5, "#1c1917"], [1, "#052e16"]],
            zmid=0,
            text=[[f"{m:.1f}%" for m in row] for row in margins],
            texttemplate="%{text}",
            colorbar=dict(title="Margin %", tickfont=dict(color="#c8d6f0")),
        ))
        fig.update_layout(
            title=f"Margin % · {h_orig} → {h_dest} · {h_ac}",
            xaxis_title="Load Factor", yaxis_title="ATF Price",
            plot_bgcolor="#0a0f1e", paper_bgcolor="#0a0f1e",
            font_color="#c8d6f0", font_family="DM Sans",
            height=420, margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
