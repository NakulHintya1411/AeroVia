"""Scenario persistence — module-level dict, no session_state dependency."""
from dataclasses import asdict

SCENARIO_KEY = "aerovia_scenarios"
MAX_SCENARIOS = 6

# Module-level store — persists for the lifetime of the Streamlit process
_store: dict = {}


def save_scenario(name: str, inputs_dict: dict, econ_dict: dict):
    # Try session_state first (preferred), fall back to module dict
    try:
        import streamlit as st
        if SCENARIO_KEY not in st.session_state:
            st.session_state[SCENARIO_KEY] = {}
        st.session_state[SCENARIO_KEY][name] = {"inputs": inputs_dict, "economics": econ_dict}
        if len(st.session_state[SCENARIO_KEY]) > MAX_SCENARIOS:
            oldest = next(iter(st.session_state[SCENARIO_KEY]))
            del st.session_state[SCENARIO_KEY][oldest]
    except Exception:
        _store[name] = {"inputs": inputs_dict, "economics": econ_dict}
        if len(_store) > MAX_SCENARIOS:
            oldest = next(iter(_store))
            del _store[oldest]


def _get_store() -> dict:
    try:
        import streamlit as st
        if SCENARIO_KEY not in st.session_state:
            st.session_state[SCENARIO_KEY] = {}
        return st.session_state[SCENARIO_KEY]
    except Exception:
        return _store


def list_scenarios() -> list:
    return list(_get_store().keys())


def get_scenario(name: str) -> dict:
    return _get_store().get(name, {})


def delete_scenario(name: str):
    store = _get_store()
    if name in store:
        del store[name]


def compare_scenarios(names: list) -> list:
    store = _get_store()
    return [{"name": n, **store[n]} for n in names if n in store]
