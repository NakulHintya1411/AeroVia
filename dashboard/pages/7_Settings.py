"""Settings — user preferences, API config, data management."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · Settings", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section
from dashboard._shared.styles import COLORS
from dashboard.utils.auth import require_auth, show_user_menu, logout
inject_css()
require_auth()

with st.sidebar:
    sidebar_logo()
    show_user_menu()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>',
                unsafe_allow_html=True)

page_header("Configuration", "Settings",
            "Manage your account, API keys, cost defaults, and data preferences.")

C = COLORS

# ── Account ───────────────────────────────────────────────────────────────────
section("Account")
a1, a2 = st.columns(2)
with a1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Signed in as</div>
        <div class="kpi-value" style="font-size:18px">{st.session_state.get('user_name','User')}</div>
        <div class="kpi-sub">@{st.session_state.get('username','')}</div>
    </div>""", unsafe_allow_html=True)
with a2:
    st.markdown("""
    <div class="kpi-card kv-accent">
        <div class="kpi-label">Plan</div>
        <div class="kpi-value" style="font-size:18px">Standard</div>
        <div class="kpi-sub">All features unlocked</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("Sign Out of AeroVia", key="settings_logout"):
    logout()

# ── AI Analyst API Key ────────────────────────────────────────────────────────
section("AI Analyst — Anthropic API Key")
st.markdown('<div class="info-panel">The AI Analyst uses Claude by Anthropic. Add your API key to enable route analysis, yield strategy advice, and market insights in natural language. Get your key at <strong>console.anthropic.com</strong></div>',
            unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

current_key = st.session_state.get("api_key", "")
col_key, col_save = st.columns([4, 1])
with col_key:
    new_key = st.text_input(
        "API Key",
        value=current_key,
        type="password",
        placeholder="sk-ant-api03-…",
        label_visibility="collapsed",
        help="Your key is stored only in your browser session — never saved to disk or GitHub"
    )
with col_save:
    if st.button("Save Key", use_container_width=True):
        if new_key.startswith("sk-ant-"):
            st.session_state["api_key"] = new_key
            st.success("API key saved for this session")
        elif new_key == "":
            st.session_state.pop("api_key", None)
            st.info("API key cleared")
        else:
            st.error("Invalid key format — should start with sk-ant-")

if current_key:
    st.caption(f"✓ Key active · {current_key[:12]}…{current_key[-4:]} · AI Analyst is ready")
else:
    st.caption("No API key set — AI Analyst will prompt for a key when you visit it")

# ── Default Cost Assumptions ──────────────────────────────────────────────────
section("Default Cost Assumptions")
st.markdown('<div class="info-panel">These values are used as defaults in the Route Builder and Route Comparison. You can override them on any individual route without changing these defaults.</div>',
            unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

from config.constants import DEFAULT_COST_ASSUMPTIONS

if "custom_defaults" not in st.session_state:
    st.session_state["custom_defaults"] = dict(DEFAULT_COST_ASSUMPTIONS)

d = st.session_state["custom_defaults"]

c1, c2, c3 = st.columns(3)
with c1:
    d["atf_price_inr_per_litre"] = st.number_input(
        "ATF Price (₹/litre)", value=float(d["atf_price_inr_per_litre"]),
        step=1.0, format="%.1f",
        help="Indian Aviation Turbine Fuel — IOCL benchmark price"
    )
    d["crew_cost_pct_of_revenue"] = st.number_input(
        "Crew Cost (% of revenue)", value=float(d["crew_cost_pct_of_revenue"]) * 100,
        step=0.5, format="%.1f",
        help="Pilot + cabin crew total compensation as % of revenue"
    ) / 100
with c2:
    d["maintenance_cost_per_flight_hour"] = st.number_input(
        "Maintenance (₹/flight hr)", value=float(d["maintenance_cost_per_flight_hour"]),
        step=500.0,
        help="Line + heavy maintenance amortised per block hour"
    )
    d["airport_charges_per_sector"] = st.number_input(
        "Airport Charges (₹/sector)", value=float(d["airport_charges_per_sector"]),
        step=500.0,
        help="Landing fees + parking + terminal charges per flight"
    )
with c3:
    d["overhead_pct_of_revenue"] = st.number_input(
        "Overhead (% of revenue)", value=float(d["overhead_pct_of_revenue"]) * 100,
        step=0.5, format="%.1f",
        help="Admin, sales, distribution, and corporate overhead"
    ) / 100
    d["avg_yield_inr_per_km"] = st.number_input(
        "Default Yield (₹/RPK)", value=float(d["avg_yield_inr_per_km"]),
        step=0.1, format="%.2f",
        help="Revenue per revenue passenger kilometre — overridden by route-specific benchmarks"
    )
    d["usd_inr_rate"] = st.number_input(
        "USD/INR Rate", value=float(d["usd_inr_rate"]),
        step=0.5, format="%.1f",
        help="Used for ownership cost conversions"
    )

col_save2, col_reset = st.columns(2)
with col_save2:
    if st.button("Save as My Defaults", use_container_width=True):
        st.session_state["custom_defaults"] = d
        st.success("Defaults saved for this session")
with col_reset:
    if st.button("Reset to Industry Benchmarks", use_container_width=True):
        st.session_state["custom_defaults"] = dict(DEFAULT_COST_ASSUMPTIONS)
        st.rerun()

# ── Data & Scenarios ──────────────────────────────────────────────────────────
section("Data & Scenarios")
from economics.scenario_store import list_scenarios, _get_store

saved = list_scenarios()
sc1, sc2 = st.columns(2)
with sc1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Saved Scenarios</div>
        <div class="kpi-value">{len(saved)}</div>
        <div class="kpi-sub">Max 6 stored at a time</div>
    </div>""", unsafe_allow_html=True)
with sc2:
    st.markdown(f"""
    <div class="kpi-card {'kv-negative' if len(saved) >= 5 else ''}">
        <div class="kpi-label">Storage Used</div>
        <div class="kpi-value">{len(saved)}/6</div>
        <div class="kpi-sub">{'Almost full — export before saving more' if len(saved) >= 5 else 'Space available'}</div>
    </div>""", unsafe_allow_html=True)

if saved:
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Saved scenarios:")
    for sc in saved:
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(f"<div style='font-size:13px;color:var(--text-2);padding:4px 0'>{sc}</div>",
                        unsafe_allow_html=True)
        with c2:
            if st.button("✕", key=f"del_{sc}", help=f"Delete {sc}"):
                from economics.scenario_store import delete_scenario
                delete_scenario(sc)
                st.rerun()

    if st.button("Clear All Scenarios", key="clear_all"):
        store = _get_store()
        store.clear()
        st.success("All scenarios cleared")
        st.rerun()

# ── About ─────────────────────────────────────────────────────────────────────
section("About AeroVia")
st.markdown("""
<div class="info-panel">
    <strong>AeroVia v2.0</strong> · Route Profitability Simulator for Indian Aviation
    <br><br>
    Built with Python · Streamlit · Plotly · Anthropic Claude API
    <br>
    Data: DGCA traffic statistics · IOCL ATF pricing · 2026 airline destination networks
    <br><br>
    <strong>Pages:</strong> Portfolio Overview · Route Builder · Scenario Lab ·
    ML Forecasts · AI Analyst · Route Comparison · P&L Dashboard · Settings
    <br><br>
    <a href="https://github.com/NakulHintya1411/AeroVia" target="_blank"
       style="color:var(--accent);font-weight:600;text-decoration:none">
        github.com/NakulHintya1411/AeroVia ↗
    </a>
</div>
""", unsafe_allow_html=True)
