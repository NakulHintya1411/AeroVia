"""AI Analyst — Claude-powered NLP chat with live route context."""
import streamlit as st
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from config.constants import INDIAN_AIRPORTS, AIRCRAFT_TYPES
from economics.engine import RouteInputs, compute_route_economics
from economics.scenario_store import list_scenarios, get_scenario


SYSTEM_PROMPT = """You are AeroVia's AI Aviation Analyst — an expert in Indian domestic airline economics.
You have deep knowledge of RASK/CASK/BELF metrics, ATF fuel pricing, DGCA regulations, Indian aviation market dynamics, and airline profitability.

When route economics data is provided in the user's message, reference it directly in your analysis.
Be concise, data-driven, and actionable. Use ₹ for Indian rupee values. Format numbers clearly (e.g. ₹12.5L, 82% LF, 14.2p RASK).
When asked about a specific route, give a structured analysis: Revenue → Costs → Profitability → Key Risks → Recommendations.
Always ground recommendations in Indian aviation context (ATF price volatility, slot availability, seasonal demand, yield management)."""


def _build_context(route_econ=None, scenario_name=None) -> str:
    parts = []
    if route_econ:
        parts.append(f"""Current Route Analysis:
- Route: {route_econ.origin} → {route_econ.destination}
- Aircraft: {route_econ.aircraft_type} ({route_econ.seats} seats)
- Distance: {route_econ.distance_km:,.0f} km | Flight Time: {route_econ.flight_time_hr:.1f}h
- Load Factor: {route_econ.load_factor:.1%} | BELF: {route_econ.belf:.1%} | Cushion: {route_econ.lf_cushion:+.1%}
- RASK: {route_econ.rask:.1f}p | CASK: {route_econ.cask:.1f}p | Margin: {route_econ.margin_pct:.1f}%
- Daily Revenue: ₹{route_econ.total_revenue_inr/1e5:.1f}L | Daily Cost: ₹{route_econ.total_cost_inr/1e5:.1f}L | Daily Profit: ₹{route_econ.profit_inr/1e5:.1f}L
- Fuel: ₹{route_econ.fuel_cost_inr/1e5:.1f}L | Crew: ₹{route_econ.crew_cost_inr/1e5:.1f}L | Maintenance: ₹{route_econ.maintenance_cost_inr/1e5:.1f}L""")

    if scenario_name:
        sc = get_scenario(scenario_name)
        if sc:
            e = sc["economics"]
            parts.append(f"Saved Scenario '{scenario_name}': Margin {e['margin_pct']:.1f}% | RASK {e['rask']:.1f}p | CASK {e['cask']:.1f}p")

    return "\n\n".join(parts)


def _call_claude(messages: list, context: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=st.session_state.get("api_key", os.environ.get("ANTHROPIC_API_KEY", "")))
        system = SYSTEM_PROMPT
        if context:
            system += f"\n\n--- Live Data Context ---\n{context}"
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        return f"⚠ API Error: {str(e)}\n\nMake sure your Anthropic API key is set correctly."


def render():
    st.title("💬 AI Analyst")
    st.caption("Ask anything about route economics, market dynamics, or profitability strategy.")

    # ── API Key setup ─────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔑 API Configuration")
        api_key = st.text_input("Anthropic API Key", type="password",
                                 value=st.session_state.get("api_key", ""),
                                 placeholder="sk-ant-...")
        if api_key:
            st.session_state["api_key"] = api_key
            st.success("API key set ✓")
        else:
            st.info("Enter your key from console.anthropic.com")

    # ── Route Context Selector ────────────────────────────────────────────────
    st.markdown('<div class="section-header">Context (Optional)</div>', unsafe_allow_html=True)
    ctx1, ctx2 = st.columns(2)
    route_econ = None

    with ctx1:
        use_route = st.toggle("Attach Live Route", value=False)
        if use_route:
            airport_options = {f"{k} — {v['city']}": k for k, v in INDIAN_AIRPORTS.items()}
            orig = airport_options[st.selectbox("Origin", list(airport_options.keys()), index=0, key="ai_orig")]
            dest_opts = {k: v for k, v in airport_options.items() if v != orig}
            dest = dest_opts[st.selectbox("Destination", list(dest_opts.keys()), index=4, key="ai_dest")]
            ac = st.selectbox("Aircraft", list(AIRCRAFT_TYPES.keys()), key="ai_ac")
            lf = st.slider("LF %", 40, 100, 82, key="ai_lf") / 100
            route_econ = compute_route_economics(RouteInputs(
                origin=orig, destination=dest, airline_code="6E",
                aircraft_type=ac, daily_frequency=3, load_factor=lf
            ))

    with ctx2:
        use_scenario = st.toggle("Attach Saved Scenario", value=False)
        scenario_name = None
        if use_scenario:
            saved = list_scenarios()
            if saved:
                scenario_name = st.selectbox("Scenario", saved)
            else:
                st.caption("No saved scenarios yet.")

    context_str = _build_context(route_econ, scenario_name)

    # Show context preview
    if context_str:
        with st.expander("📋 Context attached to this chat", expanded=False):
            st.code(context_str, language=None)

    # ── Chat Interface ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Chat</div>', unsafe_allow_html=True)

    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []

    # Quick prompts
    st.caption("Quick prompts:")
    qp_cols = st.columns(4)
    quick_prompts = [
        "Analyze this route's profitability",
        "What's driving CASK up?",
        "How can we improve BELF?",
        "Seasonal demand risks for this route",
    ]
    for i, qp in enumerate(quick_prompts):
        if qp_cols[i].button(qp, key=f"qp_{i}", use_container_width=True):
            st.session_state.ai_pending = qp

    # Display chat history
    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input
    user_input = st.chat_input("Ask about route economics, yield management, ATF impact...")

    # Handle quick prompt injection
    if "ai_pending" in st.session_state:
        user_input = st.session_state.pop("ai_pending")

    if user_input:
        if not st.session_state.get("api_key") and not os.environ.get("ANTHROPIC_API_KEY"):
            st.warning("Please enter your Anthropic API key in the sidebar to use the AI Analyst.")
        else:
            st.session_state.ai_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    response = _call_claude(st.session_state.ai_messages, context_str)
                st.write(response)

            st.session_state.ai_messages.append({"role": "assistant", "content": response})

    # Clear chat
    if st.session_state.ai_messages:
        if st.button("🗑 Clear Conversation"):
            st.session_state.ai_messages = []
            st.rerun()
