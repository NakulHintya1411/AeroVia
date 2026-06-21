import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
st.set_page_config(page_title="AeroVia", page_icon="✈", layout="wide")
from dashboard._shared.ui import inject_css
from dashboard.utils.auth import require_auth
inject_css()
require_auth()
st.switch_page("pages/0_Portfolio_Overview.py")
