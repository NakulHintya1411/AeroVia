"""Subscription plans and their limits.

Billing isn't wired up yet; every new organisation starts on "free".
`None` means unlimited.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Plan:
    key: str
    label: str
    max_scenarios: Optional[int]
    ai_messages_per_month: Optional[int]


PLANS: dict[str, Plan] = {
    "free": Plan("free", "Free", max_scenarios=6, ai_messages_per_month=30),
    "pro": Plan("pro", "Pro", max_scenarios=100, ai_messages_per_month=500),
    "team": Plan("team", "Team", max_scenarios=None, ai_messages_per_month=3000),
}

DEFAULT_PLAN = "free"


def get_plan(key: str | None) -> Plan:
    return PLANS.get(key or DEFAULT_PLAN, PLANS[DEFAULT_PLAN])
