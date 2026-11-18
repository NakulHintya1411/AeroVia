"""AeroVia authentication: sign-in / sign-up screens and the per-page auth gate."""
from __future__ import annotations

from dataclasses import asdict
from typing import Optional

import streamlit as st

from db import init_db
from services import accounts
from services.accounts import AccountError, SessionUser

_SESSION_KEY = "auth_user"


@st.cache_resource(show_spinner=False)
def _ensure_database() -> bool:
    """Apply pending migrations once per server process."""
    init_db()
    return True


def _store(user: SessionUser) -> None:
    st.session_state[_SESSION_KEY] = asdict(user)
    # Kept for pages that read these keys directly.
    st.session_state["authenticated"] = True
    st.session_state["username"] = user.email
    st.session_state["user_name"] = user.name


def current_user() -> Optional[SessionUser]:
    data = st.session_state.get(_SESSION_KEY)
    return SessionUser(**data) if data else None


def _login_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #eef2ff 0%, #f8f9fc 50%, #eff6ff 100%) !important; }
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="block-container"] { max-width: 100% !important; padding: 0 !important; }
    [data-testid="stTextInput"] input {
        background: #ffffff !important;
        border: 1.5px solid #c8d0e2 !important;
        border-radius: 8px !important;
        color: #0f1724 !important;
        font-size: 14px !important;
        height: 44px !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
    }
    [data-testid="stTextInput"] label p {
        font-size: 11px !important; font-weight: 600 !important; color: #3d4f6b !important;
        letter-spacing: 0.8px !important; text-transform: uppercase !important;
    }
    [data-testid="stFormSubmitButton"] > button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        height: 46px !important;
        width: 100% !important;
        box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover { background: #1d4ed8 !important; }
    [data-testid="stForm"] {
        background: #ffffff; border: 1px solid #e2e7f0 !important; border-radius: 16px !important;
        padding: 28px 28px 20px !important;
        box-shadow: 0 4px 24px rgba(15,23,36,0.08), 0 1px 4px rgba(15,23,36,0.04);
    }
    [data-testid="stAlert"] { border-radius: 8px !important; font-size: 13px !important; }
    </style>
    """, unsafe_allow_html=True)


def _sign_in_form() -> None:
    with st.form("sign_in", clear_on_submit=False):
        st.markdown("<div style='font-size:18px;font-weight:700;color:#0f1724;margin-bottom:2px'>"
                    "Welcome back</div><div style='font-size:13px;color:#7a8ba8;margin-bottom:12px'>"
                    "Sign in to your route analysis workspace</div>", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="you@company.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="Your password", key="login_pass")
        submitted = st.form_submit_button("Sign in →", use_container_width=True)
    if submitted:
        try:
            _store(accounts.authenticate(email, password))
            st.rerun()
        except AccountError as e:
            st.error(str(e))


def _sign_up_form() -> None:
    first_account = accounts.user_count() == 0
    with st.form("sign_up", clear_on_submit=False):
        title = "Set up AeroVia" if first_account else "Create your workspace"
        sub = ("No accounts exist yet. This first account becomes the owner."
               if first_account else "Start free. No card required.")
        st.markdown(f"<div style='font-size:18px;font-weight:700;color:#0f1724;margin-bottom:2px'>{title}</div>"
                    f"<div style='font-size:13px;color:#7a8ba8;margin-bottom:12px'>{sub}</div>",
                    unsafe_allow_html=True)
        name = st.text_input("Your name", key="su_name")
        org = st.text_input("Organisation", placeholder="e.g. Pune Airport Route Development", key="su_org")
        email = st.text_input("Work email", placeholder="you@company.com", key="su_email")
        password = st.text_input("Password", type="password",
                                 help=f"At least {accounts.MIN_PASSWORD_LENGTH} characters", key="su_pass")
        confirm = st.text_input("Confirm password", type="password", key="su_pass2")
        submitted = st.form_submit_button("Create account →", use_container_width=True)
    if submitted:
        if password != confirm:
            st.error("Passwords don't match.")
            return
        try:
            _store(accounts.register(email, name, password, org))
            st.rerun()
        except AccountError as e:
            st.error(str(e))


def login_page() -> None:
    _login_css()
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown("""
        <div style="text-align:center;margin:40px 0 24px">
            <div style="width:56px;height:56px;background:#2563eb;border-radius:14px;display:inline-flex;
                        align-items:center;justify-content:center;font-size:26px;color:#fff;margin-bottom:12px;
                        box-shadow:0 4px 16px rgba(37,99,235,0.35)">✈</div>
            <div style="font-family:'Sora',sans-serif;font-size:28px;font-weight:800;color:#0f1724;
                        letter-spacing:-0.5px;margin-bottom:4px">AeroVia</div>
            <div style="font-size:13px;color:#7a8ba8">Route Profitability Simulator</div>
        </div>""", unsafe_allow_html=True)

        if accounts.user_count() == 0:
            _sign_up_form()
        elif accounts.signup_open():
            tab_in, tab_up = st.tabs(["Sign in", "Create account"])
            with tab_in:
                _sign_in_form()
            with tab_up:
                _sign_up_form()
        else:
            _sign_in_form()
            st.caption("New here? AeroVia is invite-only right now. Ask your organisation's owner for access.")

        st.markdown("""
        <div style="text-align:center;margin-top:18px;font-size:11px;color:#b0bdd0;line-height:1.8">
            <span style="color:#2563eb;font-weight:500">Indian Aviation Economics Platform</span>
        </div>""", unsafe_allow_html=True)


def require_auth() -> SessionUser:
    """Stop the page unless someone is signed in; returns the current user."""
    _ensure_database()
    user = current_user()
    if user is not None:
        fresh = accounts.refresh(user.user_id, user.org_id)
        if fresh is not None:
            if fresh != user:
                _store(fresh)
            return fresh
        _clear_session()
    login_page()
    st.stop()


def _clear_session() -> None:
    for key in [_SESSION_KEY, "authenticated", "username", "user_name", "ai_msgs"]:
        st.session_state.pop(key, None)


def logout() -> None:
    _clear_session()
    st.rerun()


def show_user_menu() -> None:
    user = current_user()
    name = user.name if user else "User"
    org = user.org_name if user else ""
    st.sidebar.markdown(f"""
    <div style="padding:12px 16px;border-top:1px solid var(--border);margin-top:8px">
        <div style="font-size:10px;color:var(--text-4);font-weight:600;
                    text-transform:uppercase;letter-spacing:0.8px;margin-bottom:5px">Signed in as</div>
        <div style="font-size:13px;font-weight:600;color:var(--text)">{_esc(name)}</div>
        <div style="font-size:11px;color:var(--text-3)">{_esc(org)}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("Sign Out", key="logout_btn"):
        logout()


def _esc(text: str) -> str:
    import html
    return html.escape(text or "")
