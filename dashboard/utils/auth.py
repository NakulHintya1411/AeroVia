"""AeroVia Authentication — professional login page."""
import streamlit as st
import bcrypt, os

DEFAULT_USERS = {
    "nakul": {
        "name": "Nakul",
        "email": "admin@aerovia.app",
        "password": bcrypt.hashpw(b"aerovia2024", bcrypt.gensalt()).decode(),
        "role": "admin",
    }
}

def _get_users():
    try:
        users_raw = st.secrets.get("users", None)
        if users_raw:
            return dict(users_raw)
    except Exception:
        pass
    return DEFAULT_USERS

def _check_password(username: str, password: str) -> bool:
    users = _get_users()
    if username not in users:
        return False
    stored = users[username]["password"].encode()
    return bcrypt.checkpw(password.encode(), stored)

def login_page():
    # Hide sidebar completely on login
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #eef2ff 0%, #f8f9fc 50%, #eff6ff 100%) !important; }
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="block-container"] {
        max-width: 100% !important;
        padding: 0 !important;
    }
    [data-testid="stTextInput"] label { display: none !important; }
    [data-testid="stTextInput"] input {
        background: #ffffff !important;
        border: 1.5px solid #c8d0e2 !important;
        border-radius: 8px !important;
        color: #0f1724 !important;
        font-size: 14px !important;
        font-family: 'Inter', sans-serif !important;
        height: 46px !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
    }
    .stButton > button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        height: 46px !important;
        width: 100% !important;
        box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
        letter-spacing: 0.2px !important;
    }
    .stButton > button:hover {
        background: #1d4ed8 !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.4) !important;
    }
    [data-testid="stAlert"] {
        border-radius: 8px !important;
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Center the login form using columns
    _, center, _ = st.columns([1, 1.2, 1])

    with center:
        st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

        # Logo + Brand
        st.markdown("""
        <div style="text-align:center;margin-bottom:32px">
            <div style="
                width:60px;height:60px;background:#2563eb;
                border-radius:15px;display:inline-flex;
                align-items:center;justify-content:center;
                font-size:28px;margin-bottom:14px;
                box-shadow:0 4px 16px rgba(37,99,235,0.35)">✈</div>
            <div style="
                font-family:'Sora',sans-serif;font-size:28px;
                font-weight:800;color:#0f1724;
                letter-spacing:-0.5px;margin-bottom:6px">AeroVia</div>
            <div style="font-size:13px;color:#7a8ba8;font-weight:400">
                Route Profitability Simulator
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card
        st.markdown("""
        <div style="
            background:#ffffff;
            border:1px solid #e2e7f0;
            border-radius:16px;
            padding:36px 32px 28px;
            box-shadow:0 4px 24px rgba(15,23,36,0.08),0 1px 4px rgba(15,23,36,0.04)">
            <div style="
                font-family:'Inter',sans-serif;font-size:18px;
                font-weight:700;color:#0f1724;
                margin-bottom:4px;letter-spacing:-0.2px">Welcome back</div>
            <div style="font-size:13px;color:#7a8ba8;margin-bottom:28px">
                Sign in to access your route analysis workspace
            </div>
            <div style="font-size:11px;font-weight:600;color:#3d4f6b;
                        letter-spacing:0.8px;margin-bottom:6px;
                        text-transform:uppercase">Username</div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("u", placeholder="Enter your username",
                                  label_visibility="collapsed", key="login_user")

        st.markdown("""
        <div style="font-size:11px;font-weight:600;color:#3d4f6b;
                    letter-spacing:0.8px;margin:14px 0 6px;
                    text-transform:uppercase">Password</div>
        """, unsafe_allow_html=True)

        password = st.text_input("p", type="password", placeholder="Enter your password",
                                  label_visibility="collapsed", key="login_pass")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", key="login_btn", use_container_width=True):
            if _check_password(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["user_name"] = _get_users().get(username, {}).get("name", username)
                st.rerun()
            else:
                st.error("Incorrect username or password.")

        st.markdown("""
        <div style="
            text-align:center;margin-top:20px;
            padding-top:20px;border-top:1px solid #f1f4f9;
            font-size:11px;color:#b0bdd0;line-height:1.8">
            Protected by AeroVia Auth
            <span style="margin:0 5px;color:#e2e7f0">·</span>
            2FA on suspicious login
            <br>
            <span style="color:#2563eb;font-weight:500;font-size:11px">
                Indian Aviation Economics Platform
            </span>
        </div>
        """, unsafe_allow_html=True)


def require_auth():
    if st.session_state.get("authenticated"):
        return True
    login_page()
    st.stop()


def logout():
    for key in ["authenticated", "username", "user_name"]:
        st.session_state.pop(key, None)
    st.rerun()


def show_user_menu():
    name = st.session_state.get("user_name", "User")
    st.sidebar.markdown(f"""
    <div style="padding:12px 16px;border-top:1px solid var(--border);margin-top:8px">
        <div style="font-size:10px;color:var(--text-4);font-weight:600;
                    text-transform:uppercase;letter-spacing:0.8px;margin-bottom:5px">
            Signed in as
        </div>
        <div style="font-size:13px;font-weight:600;color:var(--text)">{name}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("Sign Out", key="logout_btn"):
        logout()
