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
user = require_auth()

import html
from config.plans import get_plan
from config.settings import get_settings
from services import accounts, usage

plan = get_plan(user.plan)
esc = html.escape

with st.sidebar:
    sidebar_logo()
    show_user_menu()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>',
                unsafe_allow_html=True)

page_header("Configuration", "Settings",
            "Manage your account, organisation, usage, cost defaults, and saved data.")

C = COLORS

# ── Account ───────────────────────────────────────────────────────────────────
section("Account")
a1, a2, a3 = st.columns(3)
with a1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Signed in as</div>
        <div class="kpi-value" style="font-size:18px">{esc(user.name)}</div>
        <div class="kpi-sub">{esc(user.email)}</div>
    </div>""", unsafe_allow_html=True)
with a2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Organisation</div>
        <div class="kpi-value" style="font-size:18px">{esc(user.org_name)}</div>
        <div class="kpi-sub">Your role: {esc(user.role.title())}</div>
    </div>""", unsafe_allow_html=True)
with a3:
    scen_limit = "Unlimited" if plan.max_scenarios is None else f"{plan.max_scenarios}"
    st.markdown(f"""
    <div class="kpi-card kv-accent">
        <div class="kpi-label">Plan</div>
        <div class="kpi-value" style="font-size:18px">{esc(plan.label)}</div>
        <div class="kpi-sub">{scen_limit} scenarios · {plan.ai_messages_per_month or "Unlimited"} AI messages/month</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("Sign Out of AeroVia", key="settings_logout"):
    logout()

# ── Members ───────────────────────────────────────────────────────────────────
section("Members")
members = accounts.list_members(user.org_id)
st.dataframe(
    [{"Name": m["name"], "Email": m["email"], "Role": m["role"].title(),
      "Joined": m["joined"].strftime("%d %b %Y") if m["joined"] else ""} for m in members],
    use_container_width=True, hide_index=True,
)
st.caption("Inviting teammates is coming soon.")

# ── AI Analyst usage ──────────────────────────────────────────────────────────
section("AI Analyst")
settings = get_settings()
quota = usage.ai_quota(user.org_id)
u1, u2 = st.columns(2)
with u1:
    limit_txt = "Unlimited" if quota.limit is None else f"of {quota.limit}"
    st.markdown(f"""
    <div class="kpi-card {'kv-negative' if quota.exhausted else ''}">
        <div class="kpi-label">Messages this month</div>
        <div class="kpi-value">{quota.used}</div>
        <div class="kpi-sub">{limit_txt} · resets on the 1st</div>
    </div>""", unsafe_allow_html=True)
with u2:
    status = "Ready" if settings.ai_configured else "Not configured"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Status</div>
        <div class="kpi-value" style="font-size:18px">{status}</div>
        <div class="kpi-sub">Model: {esc(settings.claude_model)}</div>
    </div>""", unsafe_allow_html=True)

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
from economics.scenario_store import list_scenarios, delete_scenario, clear_scenarios

saved = list_scenarios()
limit = plan.max_scenarios
near_full = limit is not None and len(saved) >= limit - 1
sc1, sc2 = st.columns(2)
with sc1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Saved Scenarios</div>
        <div class="kpi-value">{len(saved)}</div>
        <div class="kpi-sub">Shared with everyone in {esc(user.org_name)}</div>
    </div>""", unsafe_allow_html=True)
with sc2:
    st.markdown(f"""
    <div class="kpi-card {'kv-negative' if near_full else ''}">
        <div class="kpi-label">Storage Used</div>
        <div class="kpi-value">{len(saved)}/{'∞' if limit is None else limit}</div>
        <div class="kpi-sub">{'Almost full — delete or upgrade to save more' if near_full else 'Space available'}</div>
    </div>""", unsafe_allow_html=True)

if saved:
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Saved scenarios:")
    for i, sc in enumerate(saved):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(f"<div style='font-size:13px;color:var(--text-2);padding:4px 0'>{esc(sc)}</div>",
                        unsafe_allow_html=True)
        with c2:
            if st.button("✕", key=f"del_{i}", help=f"Delete {sc}"):
                delete_scenario(sc)
                st.rerun()

    if user.role in ("owner", "admin"):
        if st.button("Clear All Scenarios", key="clear_all"):
            clear_scenarios()
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
