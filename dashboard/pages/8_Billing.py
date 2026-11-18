"""Billing — plan, free trial, and Razorpay subscription management."""
import streamlit as st
import sys, os, html
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · Billing", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section
from dashboard.utils.auth import require_auth, show_user_menu
inject_css()
user = require_auth()

from config.plans import PLANS, get_plan
from services import billing

esc = html.escape
can_manage = user.role in ("owner", "admin")

with st.sidebar:
    sidebar_logo()
    show_user_menu()
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>',
                unsafe_allow_html=True)

page_header("Account", "Billing", "Your plan, free trial and subscription.")


def _date(dt):
    return dt.strftime("%d %b %Y") if dt else "—"


@st.cache_data(ttl=3600, show_spinner=False)
def _price(plan_key: str):
    try:
        return billing.plan_price(plan_key)
    except billing.BillingError:
        return None


def _price_text(plan_key: str) -> str:
    if plan_key == "free":
        return "₹0"
    if plan_key not in billing.get_settings().razorpay_plan_ids:
        return "—"
    p = _price(plan_key)
    if not p:
        return "See checkout"
    symbol = "₹" if p["currency"] == "INR" else f'{p["currency"]} '
    unit = {"monthly": "month", "yearly": "year", "weekly": "week", "daily": "day"}.get(p["period"], p["period"])
    every = f"/ {unit}" if p["interval"] == 1 else f"every {p['interval']} {unit}s"
    return f"{symbol}{p['amount']:,.0f} {every}"


# Pull the latest state from Razorpay (covers webhooks that haven't arrived yet).
sync_error = None
summary = billing.summary(user.org_id)
if summary.billing_configured and summary.subscription is not None:
    try:
        billing.sync_org(user.org_id)
        summary = billing.summary(user.org_id)
    except billing.BillingError as e:
        sync_error = str(e)

plan = get_plan(summary.plan_key)
sub = summary.subscription
has_paid_access = sub is not None and sub.status in billing.ACCESS_STATUSES

if not summary.billing_configured:
    st.info("Online billing isn't set up on this server yet. An administrator needs to add the Razorpay "
            "keys and plan IDs (see README → Billing).")
if sync_error:
    st.warning(f"Couldn't refresh your subscription from Razorpay: {sync_error}")

# ── Current plan ──────────────────────────────────────────────────────────────
section("Current plan")
if has_paid_access:
    source = f"Subscription · {sub.status}"
elif summary.trial_active:
    source = f"Free trial · {summary.trial_days_left} day(s) left"
else:
    source = "Free plan"

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="kpi-card kv-accent">
        <div class="kpi-label">Plan</div>
        <div class="kpi-value" style="font-size:20px">{esc(plan.label)}</div>
        <div class="kpi-sub">{esc(source)}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    if has_paid_access:
        label = "Ends on" if sub.cancel_at_period_end else "Renews on"
        value = _date(sub.current_period_end)
    elif summary.trial_active:
        label, value = "Trial ends", _date(summary.trial_ends_at)
    else:
        label, value = "Renews on", "—"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="font-size:20px">{value}</div>
        <div class="kpi-sub">{'Cancellation scheduled' if has_paid_access and sub.cancel_at_period_end else '&nbsp;'}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    scen = "Unlimited" if plan.max_scenarios is None else plan.max_scenarios
    ai = "Unlimited" if plan.ai_messages_per_month is None else plan.ai_messages_per_month
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Limits</div>
        <div class="kpi-value" style="font-size:20px">{scen} scenarios</div>
        <div class="kpi-sub">{ai} AI messages / month</div>
    </div>""", unsafe_allow_html=True)

if sub is not None:
    if sub.status == "pending":
        st.warning("Your last renewal payment failed. Razorpay is retrying it, and your plan stays active "
                   "meanwhile. Check the payment method on the email Razorpay sent you.")
    elif sub.status == "halted":
        st.error("Renewal payments failed repeatedly, so your paid plan is paused. Update your payment "
                 "method using the link in Razorpay's email to restore it.")
    elif sub.status == "created" and sub.checkout_url:
        st.info(f"You started subscribing to {get_plan(sub.plan_key).label} but haven't completed payment.")
        st.link_button("Complete payment on Razorpay →", sub.checkout_url)
    if has_paid_access and sub.cancel_at_period_end:
        trial_outlasts = bool(summary.trial_ends_at and sub.current_period_end
                              and summary.trial_ends_at > sub.current_period_end)
        st.info(f"Your {get_plan(sub.plan_key).label} plan is cancelled and ends on "
                f"{_date(sub.current_period_end)}. After that you'll move to "
                f"{'your free trial until ' + _date(summary.trial_ends_at) if trial_outlasts else 'the Free plan'}.")

# ── Plans ─────────────────────────────────────────────────────────────────────
section("Plans")
cols = st.columns(3)
for col, key in zip(cols, ["free", "pro", "team"]):
    p = PLANS[key]
    current = key == summary.plan_key
    with col:
        scen = "Unlimited" if p.max_scenarios is None else p.max_scenarios
        ai = "Unlimited" if p.ai_messages_per_month is None else p.ai_messages_per_month
        st.markdown(f"""
        <div class="kpi-card {'kv-accent' if current else ''}">
            <div class="kpi-label">{esc(p.label)}{' · current' if current else ''}</div>
            <div class="kpi-value" style="font-size:20px">{esc(_price_text(key))}</div>
            <div class="kpi-sub">{scen} saved scenarios<br>{ai} AI Analyst messages / month</div>
        </div>""", unsafe_allow_html=True)

        purchasable = key in billing.PAID_PLANS and key in billing.get_settings().razorpay_plan_ids
        if purchasable and summary.billing_configured and can_manage and not has_paid_access:
            if st.button(f"Subscribe to {p.label}", key=f"buy_{key}", use_container_width=True):
                try:
                    with st.spinner("Creating your subscription…"):
                        st.session_state["checkout"] = (key, billing.start_checkout(user.org_id, user.user_id, key))
                except billing.BillingError as e:
                    st.error(str(e))
            chk = st.session_state.get("checkout")
            if chk and chk[0] == key:
                st.link_button("Continue to secure payment →", chk[1], use_container_width=True)
                st.caption("Opens Razorpay in a new tab. Come back here after paying.")

if not can_manage:
    st.caption("Only your organisation's owner or admins can change billing.")

# ── Manage ────────────────────────────────────────────────────────────────────
if summary.billing_configured and sub is not None:
    section("Manage subscription")
    m1, m2 = st.columns(2)
    with m1:
        if st.button("Refresh status", help="Check Razorpay for the latest payment status"):
            st.session_state.pop("checkout", None)
            st.rerun()
    with m2:
        if can_manage and has_paid_access and not sub.cancel_at_period_end:
            confirm = st.checkbox(f"I want to cancel {get_plan(sub.plan_key).label} at the end of this billing period")
            if st.button("Cancel subscription", disabled=not confirm):
                try:
                    ends = billing.cancel(user.org_id)
                    st.success(f"Cancelled. You keep {get_plan(sub.plan_key).label} until {_date(ends)}.")
                    st.rerun()
                except billing.BillingError as e:
                    st.error(str(e))

st.caption("Payments are processed by Razorpay. AeroVia never sees or stores your card or UPI details.")
