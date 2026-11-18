"""Billing: free trial, Razorpay subscriptions, and the plan an organisation is on.

How an organisation's plan is decided (effective_plan_key): the best of
  * its base plan (organizations.plan, normally "free"; an admin can set a comp plan),
  * "pro" while its free trial is running,
  * the plan of any subscription whose status still grants access.

Razorpay is the source of truth for subscription state. Webhooks and the
Billing page don't trust payload contents for state; they re-fetch the
subscription from the API and store what it says, so out-of-order or replayed
webhooks can't move a subscription backwards.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Protocol

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config.plans import PLANS, get_plan
from config.settings import get_settings
from db import session_scope
from db.models import Organization, Subscription, WebhookEvent, utcnow

log = logging.getLogger(__name__)

TRIAL_PLAN = "pro"
PAID_PLANS = ("pro", "team")
PLAN_RANK = {"free": 0, "pro": 1, "team": 2}

# Statuses in which the customer keeps the paid plan. "pending" means a renewal
# charge failed and Razorpay is retrying; access continues during retries.
ACCESS_STATUSES = {"authenticated", "active", "pending"}
# Statuses that can still change at Razorpay, so they're worth re-syncing.
LIVE_STATUSES = {"created", "authenticated", "active", "pending", "halted", "paused"}

# Billing cycles to authorise. Razorpay requires a finite count; 120 monthly cycles = 10 years.
DEFAULT_TOTAL_COUNT = 120


class BillingError(Exception):
    """Raised with a message that is safe to show to the user."""


class BillingNotConfigured(BillingError):
    pass


class InvalidWebhookSignature(Exception):
    pass


class WebhookNotConfigured(Exception):
    pass


# ── Payment provider gateway ──────────────────────────────────────────────────

class Gateway(Protocol):
    def create_subscription(self, data: dict) -> dict: ...
    def fetch_subscription(self, subscription_id: str) -> dict: ...
    def cancel_subscription(self, subscription_id: str, at_cycle_end: bool) -> dict: ...
    def fetch_plan(self, plan_id: str) -> dict: ...


class RazorpayGateway:
    """Thin wrapper over the official SDK so tests can swap in a fake."""

    def __init__(self, key_id: str, key_secret: str):
        import razorpay

        self._client = razorpay.Client(auth=(key_id, key_secret))
        self._client.set_app_details({"title": "AeroVia", "version": "sprint-2"})

    def create_subscription(self, data: dict) -> dict:
        return self._call(self._client.subscription.create, data)

    def fetch_subscription(self, subscription_id: str) -> dict:
        return self._call(self._client.subscription.fetch, subscription_id)

    def cancel_subscription(self, subscription_id: str, at_cycle_end: bool) -> dict:
        return self._call(self._client.subscription.cancel, subscription_id,
                          {"cancel_at_cycle_end": bool(at_cycle_end)})

    def fetch_plan(self, plan_id: str) -> dict:
        return self._call(self._client.plan.fetch, plan_id)

    @staticmethod
    def _call(fn, *args):
        import razorpay.errors as rzp_errors
        import requests

        try:
            return fn(*args)
        except rzp_errors.BadRequestError as e:
            log.warning("Razorpay rejected a request: %s", e)
            raise BillingError(f"The payment provider rejected the request: {e}") from e
        except (rzp_errors.ServerError, rzp_errors.GatewayError) as e:
            log.warning("Razorpay server error: %s", e)
            raise BillingError("The payment provider had a problem. Please try again shortly.") from e
        except requests.RequestException as e:
            log.warning("Couldn't reach Razorpay: %s", e)
            raise BillingError("Couldn't reach the payment provider. Please try again.") from e


def default_gateway() -> Gateway:
    s = get_settings()
    if not (s.razorpay_key_id and s.razorpay_key_secret):
        raise BillingNotConfigured("Billing isn't set up on this server yet.")
    return RazorpayGateway(s.razorpay_key_id, s.razorpay_key_secret)


# ── Plan resolution ───────────────────────────────────────────────────────────

def _as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _from_unix(ts: Any) -> Optional[datetime]:
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc) if ts else None
    except (TypeError, ValueError, OSError):
        return None


def trial_end_for_new_org(now: Optional[datetime] = None) -> Optional[datetime]:
    days = get_settings().trial_days
    return (now or utcnow()) + timedelta(days=days) if days > 0 else None


def trial_active(org: Organization, now: Optional[datetime] = None) -> bool:
    ends = _as_utc(org.trial_ends_at)
    return bool(ends and ends > (now or utcnow()))


def effective_plan_key(session: Session, org: Organization, now: Optional[datetime] = None) -> str:
    keys = [org.plan if org.plan in PLANS else "free"]
    if trial_active(org, now):
        keys.append(TRIAL_PLAN)
    keys += list(session.scalars(
        select(Subscription.plan_key).where(
            Subscription.org_id == org.id, Subscription.status.in_(ACCESS_STATUSES)
        )
    ))
    return max(keys, key=lambda k: PLAN_RANK.get(k, 0))


def effective_plan_for_org_id(org_id: int) -> str:
    with session_scope() as s:
        org = s.get(Organization, org_id)
        return effective_plan_key(s, org) if org else "free"


def plan_key_for_plan_id(plan_id: Optional[str]) -> Optional[str]:
    for key, pid in get_settings().razorpay_plan_ids.items():
        if pid and pid == plan_id:
            return key
    return None


# ── Summary for the Billing page ──────────────────────────────────────────────

@dataclass(frozen=True)
class SubscriptionInfo:
    provider_subscription_id: str
    plan_key: str
    status: str
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    checkout_url: Optional[str]


@dataclass(frozen=True)
class BillingSummary:
    plan_key: str
    base_plan: str
    trial_ends_at: Optional[datetime]
    trial_active: bool
    subscription: Optional[SubscriptionInfo]  # the one granting access, else the latest live one
    billing_configured: bool

    @property
    def trial_days_left(self) -> int:
        if not (self.trial_active and self.trial_ends_at):
            return 0
        return max(0, (self.trial_ends_at - utcnow()).days + 1)


def summary(org_id: int) -> BillingSummary:
    with session_scope() as s:
        org = s.get(Organization, org_id)
        if org is None:
            raise BillingError("Organisation not found.")
        subs = list(s.scalars(
            select(Subscription).where(Subscription.org_id == org_id).order_by(Subscription.id.desc())
        ))
        current = next((x for x in subs if x.status in ACCESS_STATUSES), None) \
            or next((x for x in subs if x.status in LIVE_STATUSES), None)
        info = None
        if current is not None:
            info = SubscriptionInfo(current.provider_subscription_id, current.plan_key, current.status,
                                    _as_utc(current.current_period_end), current.cancel_at_period_end,
                                    current.checkout_url)
        return BillingSummary(
            plan_key=effective_plan_key(s, org),
            base_plan=org.plan,
            trial_ends_at=_as_utc(org.trial_ends_at),
            trial_active=trial_active(org),
            subscription=info,
            billing_configured=get_settings().billing_configured,
        )


def plan_price(plan_key: str, gateway: Optional[Gateway] = None) -> Optional[dict]:
    """Price of a paid plan as configured in Razorpay: {amount, currency, period, interval}."""
    plan_id = get_settings().razorpay_plan_ids.get(plan_key)
    if not plan_id:
        return None
    plan = (gateway or default_gateway()).fetch_plan(plan_id)
    item = plan.get("item") or {}
    return {
        "amount": (item.get("amount") or 0) / 100,  # Razorpay amounts are in paise
        "currency": item.get("currency", "INR"),
        "period": plan.get("period"),
        "interval": plan.get("interval", 1),
    }


# ── Applying provider state ───────────────────────────────────────────────────

def _apply_entity(session: Session, entity: dict) -> Optional[Subscription]:
    """Store a Razorpay subscription object. Creates the row if we haven't seen it."""
    sub_id = entity.get("id")
    if not sub_id:
        return None
    sub = session.scalar(select(Subscription).where(Subscription.provider_subscription_id == sub_id))
    plan_id = entity.get("plan_id") or ""
    notes = entity.get("notes") or {}
    if isinstance(notes, list):  # Razorpay sends [] when there are no notes
        notes = {}

    if sub is None:
        try:
            org_id = int(notes.get("org_id"))
        except (TypeError, ValueError):
            log.warning("Ignoring Razorpay subscription %s with no org_id note", sub_id)
            return None
        if session.get(Organization, org_id) is None:
            log.warning("Ignoring Razorpay subscription %s for unknown org %s", sub_id, org_id)
            return None
        plan_key = plan_key_for_plan_id(plan_id) or notes.get("plan_key")
        if plan_key not in PAID_PLANS:
            log.warning("Ignoring Razorpay subscription %s with unknown plan %s", sub_id, plan_id)
            return None
        sub = Subscription(org_id=org_id, provider_subscription_id=sub_id,
                           provider_plan_id=plan_id, plan_key=plan_key)
        session.add(sub)
    elif plan_id and plan_id != sub.provider_plan_id:
        sub.provider_plan_id = plan_id
        sub.plan_key = plan_key_for_plan_id(plan_id) or sub.plan_key

    status = entity.get("status") or sub.status or "created"
    sub.status = status
    sub.current_period_end = _from_unix(entity.get("current_end")) or sub.current_period_end
    if entity.get("short_url"):
        sub.checkout_url = entity["short_url"]
    if status in ("cancelled", "completed", "expired"):
        sub.cancel_at_period_end = False
    session.flush()
    return sub


def sync_subscription(provider_subscription_id: str, gateway: Optional[Gateway] = None) -> Optional[str]:
    """Re-fetch one subscription from Razorpay and store it. Returns its status."""
    entity = (gateway or default_gateway()).fetch_subscription(provider_subscription_id)
    with session_scope() as s:
        sub = _apply_entity(s, entity)
        return sub.status if sub else None


def sync_org(org_id: int, gateway: Optional[Gateway] = None) -> None:
    """Refresh every subscription of the org that can still change."""
    with session_scope() as s:
        ids = list(s.scalars(
            select(Subscription.provider_subscription_id).where(
                Subscription.org_id == org_id, Subscription.status.in_(LIVE_STATUSES)
            )
        ))
    if not ids:
        return
    gw = gateway or default_gateway()
    for sid in ids:
        sync_subscription(sid, gw)


# ── Customer actions ──────────────────────────────────────────────────────────

def start_checkout(org_id: int, user_id: Optional[int], plan_key: str,
                   gateway: Optional[Gateway] = None) -> str:
    """Return a Razorpay payment link for subscribing the org to `plan_key`."""
    settings = get_settings()
    if not settings.billing_configured:
        raise BillingNotConfigured("Billing isn't set up on this server yet.")
    plan_id = settings.razorpay_plan_ids.get(plan_key)
    if plan_key not in PAID_PLANS or not plan_id:
        raise BillingError("That plan isn't available.")
    gw = gateway or default_gateway()

    with session_scope() as s:
        existing = list(s.scalars(
            select(Subscription).where(Subscription.org_id == org_id, Subscription.status.in_(LIVE_STATUSES))
        ))
    for sub in existing:
        if sub.status in ACCESS_STATUSES:
            raise BillingError(
                f"Your organisation already has an active {get_plan(sub.plan_key).label} subscription. "
                "Cancel it before choosing a different plan."
            )

    # Reuse an unpaid checkout for the same plan instead of creating duplicates.
    for sub in existing:
        if sub.status == "created" and sub.provider_plan_id == plan_id:
            status = sync_subscription(sub.provider_subscription_id, gw)
            if status == "created" and sub.checkout_url:
                return sub.checkout_url
            if status in ACCESS_STATUSES:
                raise BillingError("This subscription is already paid. Refresh the page to see it.")

    entity = gw.create_subscription({
        "plan_id": plan_id,
        "total_count": DEFAULT_TOTAL_COUNT,
        "quantity": 1,
        "customer_notify": True,
        "notes": {"org_id": str(org_id), "plan_key": plan_key},
    })
    with session_scope() as s:
        sub = _apply_entity(s, entity)
        if sub is None:
            raise BillingError("The payment provider returned an unexpected response.")
        sub.created_by = user_id
        url = sub.checkout_url
    if not url:
        raise BillingError("The payment provider didn't return a payment link.")
    return url


def cancel(org_id: int, gateway: Optional[Gateway] = None) -> datetime | None:
    """Cancel the org's paid subscription at the end of the current billing period."""
    with session_scope() as s:
        sub = s.scalar(
            select(Subscription).where(Subscription.org_id == org_id,
                                       Subscription.status.in_(ACCESS_STATUSES))
            .order_by(Subscription.id.desc())
        )
        if sub is None:
            raise BillingError("There's no active subscription to cancel.")
        sid = sub.provider_subscription_id
    entity = (gateway or default_gateway()).cancel_subscription(sid, at_cycle_end=True)
    with session_scope() as s:
        sub = _apply_entity(s, entity) if entity.get("id") == sid else None
        if sub is None:
            sub = s.scalar(select(Subscription).where(Subscription.provider_subscription_id == sid))
        sub.cancel_at_period_end = sub.status not in ("cancelled", "completed", "expired")
        return _as_utc(sub.current_period_end)


# ── Webhooks ──────────────────────────────────────────────────────────────────

def verify_signature(raw_body: bytes, signature: Optional[str], secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.strip())


def handle_webhook(raw_body: bytes, signature: Optional[str], event_id: Optional[str],
                   gateway: Optional[Gateway] = None) -> str:
    """Process one Razorpay webhook delivery. Returns 'processed', 'duplicate' or 'ignored'.

    Raises InvalidWebhookSignature for forged/garbled requests and lets other
    errors propagate so the endpoint answers 5xx and Razorpay retries.
    """
    secret = get_settings().razorpay_webhook_secret
    if not secret:
        raise WebhookNotConfigured("RAZORPAY_WEBHOOK_SECRET is not set.")
    if not verify_signature(raw_body, signature, secret):
        raise InvalidWebhookSignature()

    event = json.loads(raw_body)
    event_type = str(event.get("event", ""))
    if not event_type.startswith("subscription."):
        return "ignored"
    entity = (((event.get("payload") or {}).get("subscription") or {}).get("entity")) or {}
    sub_id = entity.get("id")
    if not sub_id:
        return "ignored"

    # Razorpay can deliver an event more than once; fall back to a payload hash if
    # the event-id header is missing.
    dedupe_id = (event_id or "").strip() or "sha256:" + hashlib.sha256(raw_body).hexdigest()
    with session_scope() as s:
        if s.scalar(select(WebhookEvent.id).where(WebhookEvent.provider == "razorpay",
                                                  WebhookEvent.event_id == dedupe_id)):
            return "duplicate"

    # Source of truth is the API, not the payload (events can arrive out of order).
    # If the fetch fails, the exception propagates and Razorpay retries later.
    gw = gateway or default_gateway()
    current = gw.fetch_subscription(sub_id)

    try:
        with session_scope() as s:
            s.add(WebhookEvent(provider="razorpay", event_id=dedupe_id[:100], event_type=event_type[:60]))
            s.flush()
            _apply_entity(s, current)
    except IntegrityError:
        # A concurrent delivery of the same event got there first.
        return "duplicate"
    return "processed"
