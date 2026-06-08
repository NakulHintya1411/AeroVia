"""Scenario persistence — save, load, compare named scenarios in session."""
import json
import streamlit as st
from dataclasses import asdict


SCENARIO_KEY = "aerovia_scenarios"
MAX_SCENARIOS = 6


def _store() -> dict:
    if SCENARIO_KEY not in st.session_state:
        st.session_state[SCENARIO_KEY] = {}
    return st.session_state[SCENARIO_KEY]


def save_scenario(name: str, inputs_dict: dict, econ_dict: dict):
    store = _store()
    store[name] = {"inputs": inputs_dict, "economics": econ_dict}
    if len(store) > MAX_SCENARIOS:
        oldest = next(iter(store))
        del store[oldest]


def list_scenarios() -> list:
    return list(_store().keys())


def get_scenario(name: str) -> dict:
    return _store().get(name, {})


def delete_scenario(name: str):
    store = _store()
    if name in store:
        del store[name]


def compare_scenarios(names: list) -> list:
    store = _store()
    return [{"name": n, **store[n]} for n in names if n in store]
