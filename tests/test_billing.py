import hashlib
import hmac
import json
from datetime import timedelta

import pytest

from config.settings import get_settings
from db import session_scope
from db.models import Organization, Subscription, utcnow
from services import accounts, billing, scenarios, usage

WEBHOOK_SECRET = "whsec_test_123"
PLAN_PRO = "plan_PRO_test"
PLAN_TEAM = "plan_TEAM_test"


class FakeGateway:
    """Stands in for Razorpay. Holds subscriptions keyed by id."""

    def __init__(self):
        self.subs: dict[str, dict] = {}
        self.created: list[dict] = []
        self.cancelled: list[tuple[str, bool]] = []
        self.fail_fetch = False
        self._n = 0

    def create_subscription(self, data):
        self._n += 1
        sid = f"sub_TEST{self._n:04d}"
        entity = {"id": sid, "entity": "subscription", "plan_id": data["plan_id"], "status": "created",
                  "current_end": None, "notes": data.get("notes", {}),
                  "short_url": f"https://rzp.io/i/{sid}"}
        self.subs[sid] = entity
        self.created.append(data)
        return dict(entity)

    def fetch_subscription(self, sid):
        if self.fail_fetch:
            raise billing.BillingError("Couldn't reach the payment provider. Please try again.")
        return dict(self.subs[sid])

    def cancel_subscription(self, sid, at_cycle_end):
        self.cancelled.append((sid, at_cycle_end))
        return dict(self.subs[sid])

    def fetch_plan(self, plan_id):
        amount = 499900 if plan_id == PLAN_PRO else 1499900
        return {"id": plan_id, "period": "monthly", "interval": 1,
                "item": {"amount": amount, "currency": "INR"}}

    # helpers for tests
    def set(self, sid, **fields):
        self.subs[sid].update(fields)


@pytest.fixture
def billing_env(db, monkeypatch):
    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_key")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "rzp_test_secret")
    monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", WEBHOOK_SECRET)
    monkeypatch.setenv("RAZORPAY_PLAN_PRO", PLAN_PRO)
    monkeypatch.setenv("RAZORPAY_PLAN_TEAM", PLAN_TEAM)
    get_settings.cache_clear()
    gw = FakeGateway()
    monkeypatch.setattr(billing, "default_gateway", lambda: gw)
    return gw


def _signed(event: dict, secret: str = WEBHOOK_SECRET) -> tuple[bytes, str]:
    body = json.dumps(event).encode()
    return body, hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def _event(sid: str, event_type: str = "subscription.activated", status: str = "active", notes=None) -> dict:
    return {"entity": "event", "event": event_type, "contains": ["subscription"],
            "payload": {"subscription": {"entity": {"id": sid, "status": status, "notes": notes or {}}}}}


# ── Trial and plan resolution ─────────────────────────────────────────────────

def test_new_org_gets_pro_trial(db, monkeypatch):
    monkeypatch.setenv("AEROVIA_TRIAL_DAYS", "14")
    get_settings.cache_clear()
    u = accounts.register("t@example.com", "T", "long-enough-pw", "Trial Org")
    assert u.plan == "pro"
    s = billing.summary(u.org_id)
    assert s.trial_active and 13 <= s.trial_days_left <= 15


def test_expired_trial_falls_back_to_free(db, monkeypatch):
    monkeypatch.setenv("AEROVIA_TRIAL_DAYS", "14")
    get_settings.cache_clear()
    u = accounts.register("t@example.com", "T", "long-enough-pw", "Trial Org")
    with session_scope() as s:
        s.get(Organization, u.org_id).trial_ends_at = utcnow() - timedelta(minutes=1)
    assert accounts.refresh(u.user_id, u.org_id).plan == "free"


def test_trial_raises_scenario_limit(db, monkeypatch):
    monkeypatch.setenv("AEROVIA_TRIAL_DAYS", "14")
    get_settings.cache_clear()
    u = accounts.register("t@example.com", "T", "long-enough-pw", "Trial Org")
    for i in range(10):  # Free allows 6
        scenarios.save(u.org_id, u.user_id, f"S{i}", {}, {})
    assert len(scenarios.list_names(u.org_id)) == 10


def test_comp_plan_on_org_counts(org_user):
    with session_scope() as s:
        s.get(Organization, org_user.org_id).plan = "team"
    assert billing.effective_plan_for_org_id(org_user.org_id) == "team"
    assert usage.ai_quota(org_user.org_id).limit == 3000


@pytest.mark.parametrize("status,expected", [
    ("created", "free"), ("authenticated", "team"), ("active", "team"), ("pending", "team"),
    ("halted", "free"), ("cancelled", "free"), ("expired", "free"), ("completed", "free"),
])
def test_subscription_status_controls_access(org_user, status, expected):
    with session_scope() as s:
        s.add(Subscription(org_id=org_user.org_id, provider_subscription_id="sub_X",
                           provider_plan_id=PLAN_TEAM, plan_key="team", status=status))
    assert billing.effective_plan_for_org_id(org_user.org_id) == expected


# ── Checkout ──────────────────────────────────────────────────────────────────

def test_checkout_creates_subscription_with_org_notes(org_user, billing_env):
    url = billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    assert url.startswith("https://rzp.io/i/")
    sent = billing_env.created[0]
    assert sent["plan_id"] == PLAN_PRO
    assert sent["total_count"] == billing.DEFAULT_TOTAL_COUNT
    assert sent["notes"] == {"org_id": str(org_user.org_id), "plan_key": "pro"}
    s = billing.summary(org_user.org_id)
    assert s.subscription.status == "created"
    assert s.plan_key == "free"  # unpaid checkout grants nothing


def test_checkout_reuses_unpaid_link(org_user, billing_env):
    first = billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    second = billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    assert first == second
    assert len(billing_env.created) == 1


def test_checkout_refused_while_subscribed(org_user, billing_env):
    billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    billing_env.set("sub_TEST0001", status="active")
    billing.sync_org(org_user.org_id)
    with pytest.raises(billing.BillingError, match="already has an active"):
        billing.start_checkout(org_user.org_id, org_user.user_id, "team")


def test_checkout_requires_configuration(org_user):
    with pytest.raises(billing.BillingNotConfigured):
        billing.start_checkout(org_user.org_id, org_user.user_id, "pro")


def test_unknown_plan_rejected(org_user, billing_env):
    with pytest.raises(billing.BillingError, match="isn't available"):
        billing.start_checkout(org_user.org_id, org_user.user_id, "free")


def test_sync_activates_plan_and_period_end(org_user, billing_env):
    billing.start_checkout(org_user.org_id, org_user.user_id, "team")
    billing_env.set("sub_TEST0001", status="active", current_end=1893456000)  # 2030-01-01
    billing.sync_org(org_user.org_id)
    s = billing.summary(org_user.org_id)
    assert s.plan_key == "team"
    assert s.subscription.current_period_end.year == 2030
    assert accounts.refresh(org_user.user_id, org_user.org_id).plan == "team"


def test_cancel_at_period_end(org_user, billing_env):
    billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    billing_env.set("sub_TEST0001", status="active", current_end=1893456000)
    billing.sync_org(org_user.org_id)
    ends = billing.cancel(org_user.org_id)
    assert billing_env.cancelled == [("sub_TEST0001", True)]
    assert ends.year == 2030
    s = billing.summary(org_user.org_id)
    assert s.subscription.cancel_at_period_end and s.plan_key == "pro"  # access until period end

    billing_env.set("sub_TEST0001", status="cancelled")
    billing.sync_org(org_user.org_id)
    assert billing.summary(org_user.org_id).plan_key == "free"


def test_cancel_without_subscription(org_user, billing_env):
    with pytest.raises(billing.BillingError, match="no active subscription"):
        billing.cancel(org_user.org_id)


def test_plan_price_from_razorpay(org_user, billing_env):
    p = billing.plan_price("pro")
    assert p == {"amount": 4999.0, "currency": "INR", "period": "monthly", "interval": 1}


# ── Webhooks ──────────────────────────────────────────────────────────────────

def test_webhook_rejects_bad_signature(org_user, billing_env):
    body, _ = _signed(_event("sub_TEST0001"))
    with pytest.raises(billing.InvalidWebhookSignature):
        billing.handle_webhook(body, "deadbeef", "evt_1")
    with pytest.raises(billing.InvalidWebhookSignature):
        billing.handle_webhook(body, None, "evt_1")
    _, wrong = _signed(_event("sub_TEST0001"), secret="other-secret")
    with pytest.raises(billing.InvalidWebhookSignature):
        billing.handle_webhook(body, wrong, "evt_1")


def test_webhook_requires_secret(org_user, monkeypatch):
    body, sig = _signed(_event("sub_X"))
    with pytest.raises(billing.WebhookNotConfigured):
        billing.handle_webhook(body, sig, "evt_1")


def test_webhook_applies_state_from_api_not_payload(org_user, billing_env):
    billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    billing_env.set("sub_TEST0001", status="active")
    # A stale event claiming "cancelled" arrives; the API says active.
    body, sig = _signed(_event("sub_TEST0001", "subscription.cancelled", status="cancelled"))
    assert billing.handle_webhook(body, sig, "evt_1") == "processed"
    assert billing.summary(org_user.org_id).subscription.status == "active"


def test_webhook_is_idempotent(org_user, billing_env):
    billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    billing_env.set("sub_TEST0001", status="active")
    body, sig = _signed(_event("sub_TEST0001"))
    assert billing.handle_webhook(body, sig, "evt_same") == "processed"
    assert billing.handle_webhook(body, sig, "evt_same") == "duplicate"
    # Without an event-id header, the body hash is used instead.
    assert billing.handle_webhook(body, sig, None) == "processed"
    assert billing.handle_webhook(body, sig, None) == "duplicate"


def test_webhook_creates_unknown_subscription_from_notes(org_user, billing_env):
    billing_env.subs["sub_EXT1"] = {"id": "sub_EXT1", "plan_id": PLAN_TEAM, "status": "active",
                                    "notes": {"org_id": str(org_user.org_id), "plan_key": "team"}}
    body, sig = _signed(_event("sub_EXT1"))
    assert billing.handle_webhook(body, sig, "evt_2") == "processed"
    assert billing.effective_plan_for_org_id(org_user.org_id) == "team"


def test_webhook_ignores_subscription_for_unknown_org(org_user, billing_env):
    billing_env.subs["sub_EXT2"] = {"id": "sub_EXT2", "plan_id": PLAN_TEAM, "status": "active",
                                    "notes": {"org_id": "99999"}}
    body, sig = _signed(_event("sub_EXT2"))
    billing.handle_webhook(body, sig, "evt_3")
    assert billing.effective_plan_for_org_id(org_user.org_id) == "free"


def test_webhook_ignores_other_events(org_user, billing_env):
    body, sig = _signed({"event": "payment.captured", "payload": {}})
    assert billing.handle_webhook(body, sig, "evt_4") == "ignored"


def test_webhook_fetch_failure_is_not_marked_processed(org_user, billing_env):
    billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    billing_env.set("sub_TEST0001", status="active")
    billing_env.fail_fetch = True
    body, sig = _signed(_event("sub_TEST0001"))
    with pytest.raises(billing.BillingError):
        billing.handle_webhook(body, sig, "evt_retry")
    # Razorpay retries; this time it works because the event wasn't recorded.
    billing_env.fail_fetch = False
    assert billing.handle_webhook(body, sig, "evt_retry") == "processed"
    assert billing.effective_plan_for_org_id(org_user.org_id) == "pro"


def test_organisations_cannot_cancel_each_other(org_user, billing_env):
    billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    billing_env.set("sub_TEST0001", status="active")
    billing.sync_org(org_user.org_id)
    other = accounts.register("o@example.com", "O", "long-enough-pw", "Other")
    with pytest.raises(billing.BillingError, match="no active subscription"):
        billing.cancel(other.org_id)
    assert billing_env.cancelled == []
