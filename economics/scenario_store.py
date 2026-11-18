"""Scenario storage for the dashboard pages.

Thin wrapper over `services.scenarios` that fills in the signed-in user's
organisation, so pages keep calling `save_scenario(...)`, `list_scenarios()` etc.
Scenarios live in the database and survive refreshes, sign-outs and restarts.
"""
from __future__ import annotations

from services import scenarios as _svc
from services.scenarios import ScenarioError, ScenarioLimitReached  # noqa: F401  (re-exported)


def _who() -> tuple[int, int]:
    from dashboard.utils.auth import current_user

    user = current_user()
    if user is None:
        raise RuntimeError("No signed-in user; call require_auth() first.")
    return user.org_id, user.user_id


def save_scenario(name: str, inputs_dict: dict, econ_dict: dict) -> None:
    org_id, user_id = _who()
    _svc.save(org_id, user_id, name, inputs_dict, econ_dict)


def list_scenarios() -> list:
    return _svc.list_names(_who()[0])


def get_scenario(name: str) -> dict:
    return _svc.get(_who()[0], name)


def delete_scenario(name: str) -> None:
    _svc.remove(_who()[0], name)


def clear_scenarios() -> None:
    _svc.clear(_who()[0])


def compare_scenarios(names: list) -> list:
    return _svc.compare(_who()[0], names)
