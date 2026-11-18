"""Usage metering per organisation (AI messages for now)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select

from config.plans import get_plan
from db import session_scope
from db.models import Organization, UsageEvent

AI_MESSAGE = "ai_message"


@dataclass(frozen=True)
class Quota:
    used: int
    limit: Optional[int]  # None = unlimited

    @property
    def remaining(self) -> Optional[int]:
        return None if self.limit is None else max(0, self.limit - self.used)

    @property
    def exhausted(self) -> bool:
        return self.limit is not None and self.used >= self.limit


def month_start(now: Optional[datetime] = None) -> datetime:
    now = now or datetime.now(timezone.utc)
    return now.astimezone(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def record(org_id: int, user_id: Optional[int], kind: str, model: Optional[str] = None,
           input_tokens: int = 0, output_tokens: int = 0) -> None:
    with session_scope() as s:
        s.add(UsageEvent(org_id=org_id, user_id=user_id, kind=kind, model=model,
                         input_tokens=int(input_tokens or 0), output_tokens=int(output_tokens or 0)))


def count_this_month(org_id: int, kind: str, now: Optional[datetime] = None) -> int:
    with session_scope() as s:
        return s.scalar(
            select(func.count(UsageEvent.id)).where(
                UsageEvent.org_id == org_id,
                UsageEvent.kind == kind,
                UsageEvent.created_at >= month_start(now),
            )
        ) or 0


def ai_quota(org_id: int) -> Quota:
    with session_scope() as s:
        org = s.get(Organization, org_id)
        plan = get_plan(org.plan if org else None)
    return Quota(used=count_this_month(org_id, AI_MESSAGE), limit=plan.ai_messages_per_month)
