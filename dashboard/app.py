"""AeroVia — Route Profitability Simulator
Main Streamlit entry point.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="AeroVia",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main { background: #0a0f1e; }
[data-testid="stSidebar"] { background: #0d1426; border-right: 1px solid #1e2d4a; }
[data-testid="stSidebar"] * { color: #c8d6f0 !important; }

.metric-card {
    background: linear-gradient(135deg, #111c35 0%, #0d1626 100%);
    border: 1px solid #1e3058;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.metric-label { font-size: 11px; font-weight: 600; letter-spacing: 1.5px; color: #5b7fa6; text-transform: uppercase; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 28px; font-weight: 700; color: #e8f0ff; margin-top: 4px; }
.metric-delta { font-size: 13px; margin-top: 6px; }
.delta-pos { color: #34d399; }
.delta-neg { color: #f87171; }

.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #3b82f6;
    text-transform: uppercase;
    margin: 24px 0 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e3058;
}
.profit-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.badge-profit { background: #052e16; color: #34d399; border: 1px solid #166534; }
.badge-loss { background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }
.badge-break { background: #1c1917; color: #fbbf24; border: 1px solid #78350f; }

.route-tag {
    background: #111c35;
    border: 1px solid #253a5c;
    border-radius: 6px;
    padding: 6px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    color: #93c5fd;
    display: inline-block;
}
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #3b82f6);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.stButton > button:hover { background: linear-gradient(135deg, #1e40af, #2563eb); }
h1 { font-family: 'Space Mono', monospace !important; color: #e8f0ff !important; font-size: 24px !important; }
h2 { font-family: 'DM Sans', sans-serif !important; color: #c8d6f0 !important; font-size: 18px !important; font-weight: 600 !important; }
h3 { font-family: 'DM Sans', sans-serif !important; color: #93b4d8 !important; font-size: 14px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

from dashboard.pages import route_builder, scenario_lab, portfolio, ml_forecast, ai_analyst

PAGES = {
    "🗺 Portfolio Overview": portfolio,
    "✈ Route Builder": route_builder,
    "⚗ Scenario Lab": scenario_lab,
    "🤖 ML Forecasts": ml_forecast,
    "💬 AI Analyst": ai_analyst,
}

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✈ **AeroVia**")
    st.caption("Route Profitability Simulator")
    st.divider()
    page_name = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.caption("v2.0 · Built for Indian Aviation")

PAGES[page_name].render()
