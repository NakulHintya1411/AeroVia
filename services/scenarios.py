"""Saved route scenarios, scoped to an organisation.

Every function takes `org_id` and filters by it, so one customer can never
read or change another customer's scenarios.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy import delete, func, select

from config.plans import get_plan
from db import session_scope
from db.models import Organization, Scenario

MAX_NAME_LENGTH = 200


class ScenarioError(ValueError):
    """A problem the user can fix; the message is safe to show them."""


class ScenarioLimitReached(ScenarioError):
    pass


def _jsonable(data: dict) -> dict[str, Any]:
    # Round-trip through JSON so numpy scalars etc. become plain types.
    return json.loads(json.dumps(data, default=float))


def save(org_id: int, user_id: Optional[int], name: str, inputs: dict, economics: dict) -> None:
    """Create a scenario, or overwrite the one with the same name."""
    name = (name or "").strip()
    if not name:
        raise ScenarioError("Give the scenario a name.")
    if len(name) > MAX_NAME_LENGTH:
        raise ScenarioError(f"Scenario names must be {MAX_NAME_LENGTH} characters or fewer.")

    with session_scope() as s:
        existing = s.scalar(select(Scenario).where(Scenario.org_id == org_id, Scenario.name == name))
        if existing is not None:
            existing.inputs = _jsonable(inputs)
            existing.economics = _jsonable(economics)
            return

        org = s.get(Organization, org_id)
        if org is None:
            raise ScenarioError("Organisation not found.")
        plan = get_plan(org.plan)
        if plan.max_scenarios is not None:
            count = s.scalar(select(func.count(Scenario.id)).where(Scenario.org_id == org_id)) or 0
            if count >= plan.max_scenarios:
                raise ScenarioLimitReached(
                    f"Your {plan.label} plan stores up to {plan.max_scenarios} scenarios. "
                    "Delete one or upgrade to save more."
                )
        s.add(Scenario(org_id=org_id, created_by=user_id, name=name,
                       inputs=_jsonable(inputs), economics=_jsonable(economics)))


def list_names(org_id: int) -> list[str]:
    with session_scope() as s:
        return list(s.scalars(
            select(Scenario.name).where(Scenario.org_id == org_id).order_by(Scenario.created_at, Scenario.id)
        ))


def get(org_id: int, name: str) -> dict:
    with session_scope() as s:
        sc = s.scalar(select(Scenario).where(Scenario.org_id == org_id, Scenario.name == name))
        return {"inputs": sc.inputs, "economics": sc.economics} if sc else {}


def compare(org_id: int, names: list[str]) -> list[dict]:
    """Scenarios for `names`, in the order given; unknown names are skipped."""
    if not names:
        return []
    with session_scope() as s:
        rows = s.scalars(select(Scenario).where(Scenario.org_id == org_id, Scenario.name.in_(names)))
        by_name = {r.name: {"name": r.name, "inputs": r.inputs, "economics": r.economics} for r in rows}
    return [by_name[n] for n in names if n in by_name]


def remove(org_id: int, name: str) -> None:
    with session_scope() as s:
        s.execute(delete(Scenario).where(Scenario.org_id == org_id, Scenario.name == name))


def clear(org_id: int) -> None:
    with session_scope() as s:
        s.execute(delete(Scenario).where(Scenario.org_id == org_id))
