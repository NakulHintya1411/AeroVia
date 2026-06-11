"""AI Analyst — Streamlit page."""
import streamlit as st
import sys, os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _root)

st.set_page_config(page_title="AeroVia · AI Analyst", page_icon="✈", layout="wide")

from dashboard._shared.ui import inject_css, sidebar_logo, page_header, section
from dashboard._shared.styles import COLORS
inject_css()

from config.constants import INDIAN_AIRPORTS, AIRCRAFT_TYPES
from economics.engine import RouteInputs, compute_route_economics
from economics.scenario_store import list_scenarios, get_scenario

with st.sidebar:
    sidebar_logo()
    st.markdown('<div class="sec-label" style="margin:18px 0 8px;padding:0 8px">API Key</div>', unsafe_allow_html=True)
    kv = st.text_input("Anthropic API Key", type="password",
                        value=st.session_state.get("api_key",""),
                        placeholder="sk-ant-…", label_visibility="collapsed")
    if kv:
        st.session_state["api_key"] = kv
        st.success("API key active")
    else:
        st.markdown('<div class="info-panel" style="margin:0 8px">Get your key at<br>console.anthropic.com</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-footer"><div class="sidebar-version">v2.0 · Indian Aviation</div></div>', unsafe_allow_html=True)

page_header("Intelligence Layer", "AI Analyst",
            "Ask anything about route economics, yield strategy, competitive dynamics, or market outlook.")

C = COLORS
SYSTEM_PROMPT = """You are AeroVia's AI Aviation Analyst — an expert in Indian domestic airline economics with deep command of RASK/CASK/BELF frameworks, ATF pricing dynamics, DGCA regulations, yield management, and Indian aviation market structure (IndiGo, Air India, SpiceJet, Akasa, UDAN scheme, slot constraints at metro airports).

When route data is provided in the context below, reference it directly in your analysis.
Be concise, data-driven, and actionable. Use ₹ for currency. Format key numbers clearly (₹12.5L, 82% LF, 14.2p RASK).
For route analyses structure your response as: Revenue Assessment → Cost Drivers → Profitability Verdict → Key Risks → Recommendations."""

def _ctx(econ=None, sc_name=None):
    parts = []
    if econ:
        parts.append(f"Route: {econ.origin}→{econ.destination} | {econ.aircraft_type} | {econ.distance_km:.0f}km | {econ.flight_time_hr:.1f}h\nLF: {econ.load_factor:.1%} | BELF: {econ.belf:.1%} | Cushion: {econ.lf_cushion:+.1%}\nRASK: {econ.rask:.1f}p | CASK: {econ.cask:.1f}p | Margin: {econ.margin_pct:.1f}%\nRevenue: ₹{econ.total_revenue_inr/1e5:.1f}L | Cost: ₹{econ.total_cost_inr/1e5:.1f}L | Profit: ₹{econ.profit_inr/1e5:.1f}L\nFuel: ₹{econ.fuel_cost_inr/1e5:.1f}L | Crew: ₹{econ.crew_cost_inr/1e5:.1f}L | Maint: ₹{econ.maintenance_cost_inr/1e5:.1f}L")
    if sc_name:
        sc = get_scenario(sc_name)
        if sc:
            e = sc["economics"]
            parts.append(f"Scenario '{sc_name}': {e['origin']}→{e['destination']} | Margin {e['margin_pct']:.1f}% | RASK {e['rask']:.1f}p | CASK {e['cask']:.1f}p")
    return "\n\n".join(parts)

def _call(messages, ctx):
    try:
        import anthropic
        key = st.session_state.get("api_key") or os.environ.get("ANTHROPIC_API_KEY","")
        client = anthropic.Anthropic(api_key=key)
        sys_p = SYSTEM_PROMPT + (f"\n\n--- LIVE ROUTE DATA ---\n{ctx}" if ctx else "")
        r = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1024,
                                    system=sys_p, messages=messages)
        return r.content[0].text
    except Exception as e:
        return f"⚠ Error: {e}"

section("Context")
ctx1, ctx2 = st.columns(2)
econ = None
with ctx1:
    use_route = st.toggle("Attach live route", value=False)
    if use_route:
        ap = {f"{k} — {v['city']}": k for k, v in INDIAN_AIRPORTS.items()}
        ao = ap[st.selectbox("Origin", list(ap.keys()), index=0, key="ai_o")]
        dopts = {k:v for k,v in ap.items() if v!=ao}
        ad = dopts[st.selectbox("Destination", list(dopts.keys()), index=4, key="ai_d")]
        aac = st.selectbox("Aircraft", list(AIRCRAFT_TYPES.keys()), key="ai_ac")
        alf = st.slider("Load Factor %", 40, 100, 82, key="ai_lf") / 100
        econ = compute_route_economics(RouteInputs(ao, ad, "6E", aac, 3, alf))
with ctx2:
    use_sc = st.toggle("Attach saved scenario", value=False)
    sc_name = None
    if use_sc:
        saved = list_scenarios()
        if saved: sc_name = st.selectbox("Scenario", saved, label_visibility="collapsed")
        else: st.caption("No saved scenarios yet.")

ctx_str = _ctx(econ, sc_name)
if ctx_str:
    with st.expander("Context attached to this conversation", expanded=False):
        st.code(ctx_str, language=None)

section("Quick Prompts")
qcols = st.columns(4)
prompts = ["Analyze this route's profitability", "What's driving CASK up?",
           "How do we get BELF below 70%?", "What are the seasonal demand risks?"]
for i, qp in enumerate(prompts):
    if qcols[i].button(qp, key=f"qp_{i}", use_container_width=True):
        st.session_state["ai_p"] = qp

section("Conversation")
if "ai_msgs" not in st.session_state:
    st.session_state.ai_msgs = []

for msg in st.session_state.ai_msgs:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_in = st.chat_input("Ask about routes, yields, ATF impact, competitive positioning…")
if "ai_p" in st.session_state:
    user_in = st.session_state.pop("ai_p")

if user_in:
    if not (st.session_state.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")):
        st.warning("Add your Anthropic API key in the sidebar to use the AI Analyst.")
    else:
        st.session_state.ai_msgs.append({"role":"user","content":user_in})
        with st.chat_message("user"): st.write(user_in)
        with st.chat_message("assistant"):
            with st.spinner(""):
                resp = _call(st.session_state.ai_msgs, ctx_str)
            st.write(resp)
        st.session_state.ai_msgs.append({"role":"assistant","content":resp})

if st.session_state.ai_msgs:
    if st.button("Clear conversation"):
        st.session_state.ai_msgs = []; st.rerun()
