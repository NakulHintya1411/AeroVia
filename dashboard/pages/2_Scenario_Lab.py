"""Scenario Lab — Streamlit page."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · Scenario Lab", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section, kpi_row, apply_theme
from dashboard._shared.styles import COLORS
inject_css()

import plotly.graph_objects as go
import pandas as pd, numpy as np
from config.constants import INDIAN_AIRPORTS, AIRCRAFT_TYPES
from economics.engine import RouteInputs, compute_route_economics
from economics.scenario_store import list_scenarios, compare_scenarios, delete_scenario

with st.sidebar:
    sidebar_logo()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>', unsafe_allow_html=True)

page_header("What-If Analysis", "Scenario Lab",
            "Live parameter sweeps, saved scenario comparisons, and full sensitivity heatmaps.")

C = COLORS
ap = {f"{k} — {v['city']}": k for k, v in INDIAN_AIRPORTS.items()}
tab1, tab2, tab3 = st.tabs(["Live What-If", "Compare Scenarios", "Sensitivity Heatmap"])

with tab1:
    section("Base Route")
    b1,b2,b3,b4 = st.columns(4)
    with b1: orig = ap[st.selectbox("Origin", list(ap.keys()), index=0, key="wi_o")]
    with b2:
        dopts = {k:v for k,v in ap.items() if v!=orig}
        dest = dopts[st.selectbox("Destination", list(dopts.keys()), index=4, key="wi_d")]
    with b3: ac = st.selectbox("Aircraft", list(AIRCRAFT_TYPES.keys()), key="wi_ac")
    with b4: freq = st.number_input("Flights/day", 1, 12, 3, key="wi_freq")

    section("What-If Parameters")
    s1,s2,s3 = st.columns(3)
    with s1:
        lf_w = st.slider("Load Factor (%)", 40, 100, 82, key="wi_lf") / 100
        atf_w = st.slider("ATF Price (₹/L)", 60, 140, 95, key="wi_atf", step=1)
    with s2:
        yield_w = st.slider("Yield (₹/RPK)", 2.0, 8.0, 4.2, step=0.1, key="wi_y")
        crew_w = st.slider("Crew Cost (%)", 5, 20, 12, key="wi_crew") / 100
    with s3:
        freq_w = st.slider("Frequency", 1, 12, freq, key="wi_freq2")
        oh_w = st.slider("Overhead (%)", 3, 15, 8, key="wi_oh") / 100

    base = compute_route_economics(RouteInputs(orig,dest,"6E",ac,freq,0.82,
                                               atf_price_inr_per_litre=95,yield_inr_per_km=4.2,
                                               crew_cost_pct=0.12,overhead_pct=0.08))
    what = compute_route_economics(RouteInputs(orig,dest,"6E",ac,freq_w,lf_w,
                                               atf_price_inr_per_litre=float(atf_w),
                                               yield_inr_per_km=yield_w,
                                               crew_cost_pct=crew_w,overhead_pct=oh_w))

    section("Impact vs Base Case")
    def di(label, bv, wv, fmt=".1f", suf="", flip=False):
        d = wv - bv
        pos = (d >= 0) if not flip else (d <= 0)
        return {"label":label,"value":f"{wv:{fmt}}{suf}","delta":f"{abs(d):{fmt}}{suf}",
                "delta_pos":pos,"variant":"positive" if pos else "negative"}

    kpi_row([
        di("Net Margin",   base.margin_pct,   what.margin_pct,   ".1f", "%"),
        di("RASK (p)",     base.rask,         what.rask,         ".1f", "p"),
        di("CASK (p)",     base.cask,         what.cask,         ".1f", "p", flip=True),
        di("Daily Profit", base.profit_inr/1e5, what.profit_inr/1e5, ".1f", "L"),
    ])

    fig = go.Figure()
    metrics = ["RASK","CASK","Margin %","BELF %"]
    bv = [base.rask, base.cask, base.margin_pct, base.belf*100]
    wv = [what.rask, what.cask, what.margin_pct, what.belf*100]
    fig.add_trace(go.Bar(name="Base Case", x=metrics, y=bv, marker_color=C["border"], marker_line_width=0))
    fig.add_trace(go.Bar(name="What-If",   x=metrics, y=wv, marker_color=C["accent"], marker_line_width=0))
    apply_theme(fig, "Base Case vs What-If", 300)
    fig.update_layout(barmode="group")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    saved = list_scenarios()
    if not saved:
        st.markdown('<div class="info-panel">No saved scenarios yet — build and save routes in the Route Builder first.</div>', unsafe_allow_html=True)
    else:
        selected = st.multiselect("Select scenarios to compare", saved,
                                   default=saved[:min(4,len(saved))], label_visibility="collapsed")
        if selected:
            scenarios = compare_scenarios(selected)
            rows = [{"Scenario":sc["name"],
                     "Route":f"{sc['economics']['origin']} → {sc['economics']['destination']}",
                     "Aircraft":sc["economics"]["aircraft_type"],
                     "LF":f"{sc['economics']['load_factor']*100:.0f}%",
                     "RASK":f"{sc['economics']['rask']:.1f}p",
                     "CASK":f"{sc['economics']['cask']:.1f}p",
                     "Margin":f"{sc['economics']['margin_pct']:.1f}%",
                     "BELF":f"{sc['economics']['belf']*100:.1f}%",
                     "Daily Profit":f"₹{sc['economics']['profit_inr']/1e5:.1f}L"}
                    for sc in scenarios]
            st.dataframe(pd.DataFrame(rows).set_index("Scenario"), use_container_width=True)

            fig2 = go.Figure()
            for sc in scenarios:
                e = sc["economics"]
                color = C["green"] if e["margin_pct"] > 0 else C["red"]
                fig2.add_trace(go.Scatter(
                    x=[e["cask"]], y=[e["rask"]], mode="markers+text",
                    marker=dict(size=14, color=color, line=dict(color=C["border"], width=1.5)),
                    text=[sc["name"][:22]], textposition="top center",
                    textfont=dict(size=10, color=C["text3"]),
                    hovertemplate=f"RASK: {e['rask']:.1f}p | CASK: {e['cask']:.1f}p | Margin: {e['margin_pct']:.1f}%<extra>{sc['name']}</extra>",
                    showlegend=False,
                ))
            all_c = [s["economics"]["cask"] for s in scenarios]
            lr = [min(all_c)*0.9, max(all_c)*1.1]
            fig2.add_trace(go.Scatter(x=lr, y=lr, mode="lines",
                                       line=dict(color=C["amber"], dash="dash", width=1.5),
                                       name="Break-Even"))
            apply_theme(fig2, "RASK vs CASK  —  above the diagonal is profitable", 360)
            fig2.update_layout(xaxis_title="CASK (p/ASK)", yaxis_title="RASK (p/ASK)")
            st.plotly_chart(fig2, use_container_width=True)

            ca, cb = st.columns(2)
            with ca:
                to_del = st.selectbox("Delete scenario", ["—"]+saved, label_visibility="collapsed")
                if to_del != "—" and st.button("Delete"): delete_scenario(to_del); st.rerun()
            with cb:
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("↓ Export CSV", pd.DataFrame(rows).to_csv(index=False),
                                    "aerovia_compare.csv", "text/csv")

with tab3:
    section("Parameters")
    h1,h2,h3 = st.columns(3)
    with h1: ho = ap[st.selectbox("Origin", list(ap.keys()), index=0, key="hm_o")]
    with h2:
        hdopts = {k:v for k,v in ap.items() if v!=ho}
        hd = hdopts[st.selectbox("Destination", list(hdopts.keys()), index=4, key="hm_d")]
    with h3: hac = st.selectbox("Aircraft", list(AIRCRAFT_TYPES.keys()), key="hm_ac")

    lf_r = [lf/100 for lf in range(55, 96, 5)]
    atf_r = list(range(75, 126, 5))
    margins = []
    for av in atf_r:
        row = [compute_route_economics(RouteInputs(ho,hd,"6E",hac,3,lv,
               atf_price_inr_per_litre=float(av))).margin_pct for lv in lf_r]
        margins.append(row)

    colorscale = [[0,"#fef2f2"],[0.35,"#fca5a5"],[0.47,"#fde68a"],
                  [0.5,"#f8f9fc"],[0.53,"#d1fae5"],[0.8,"#6ee7b7"],[1.0,"#059669"]]
    fig3 = go.Figure(go.Heatmap(
        z=margins, x=[f"{lf*100:.0f}%" for lf in lf_r], y=[f"₹{a}/L" for a in atf_r],
        colorscale=colorscale, zmid=0,
        text=[[f"{m:.1f}%" for m in row] for row in margins],
        texttemplate="%{text}", textfont=dict(size=10),
        colorbar=dict(title=dict(text="Margin %", font=dict(size=11,color=C["text3"])),
                      tickfont=dict(size=10,color=C["text3"]), thickness=14),
        hovertemplate="ATF: %{y} | LF: %{x}<br>Margin: %{z:.1f}%<extra></extra>",
    ))
    fig3.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(color=C["text3"],family="Inter, sans-serif",size=11),
        title=dict(text=f"Margin %  ·  {ho} → {hd}  ·  {hac}",
                   font=dict(size=12,color=C["text3"]),x=0),
        xaxis_title="Load Factor", yaxis_title="ATF Price",
        height=440, margin=dict(l=14,r=14,t=44,b=14),
    )
    st.plotly_chart(fig3, use_container_width=True)
