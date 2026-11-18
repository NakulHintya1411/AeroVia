import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from services import billing
from tests.test_billing import WEBHOOK_SECRET, billing_env  # noqa: F401  (fixture)


@pytest.fixture
def client(db):
    from api.main import app

    with TestClient(app) as c:
        yield c


def _post(client, event: dict, secret: str = WEBHOOK_SECRET, event_id: str = "evt_api_1"):
    body = json.dumps(event).encode()
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post("/webhooks/razorpay", content=body,
                       headers={"X-Razorpay-Signature": sig, "x-razorpay-event-id": event_id,
                                "Content-Type": "application/json"})


def _event(sid):
    return {"event": "subscription.activated",
            "payload": {"subscription": {"entity": {"id": sid, "status": "active"}}}}


def test_healthz(client):
    assert client.get("/healthz").json() == {"status": "ok"}


def test_docs_are_not_exposed(client):
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_webhook_not_configured_returns_503(client):
    assert _post(client, _event("sub_1")).status_code == 503


def test_webhook_bad_signature_returns_400(client, billing_env):
    r = _post(client, _event("sub_1"), secret="wrong")
    assert r.status_code == 400


def test_webhook_processes_and_dedupes(client, billing_env, org_user):
    billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    billing_env.set("sub_TEST0001", status="active")
    r = _post(client, _event("sub_TEST0001"))
    assert r.status_code == 200 and r.json() == {"status": "processed"}
    assert billing.effective_plan_for_org_id(org_user.org_id) == "pro"
    assert _post(client, _event("sub_TEST0001")).json() == {"status": "duplicate"}


def test_webhook_provider_outage_returns_500_for_retry(client, billing_env, org_user):
    billing.start_checkout(org_user.org_id, org_user.user_id, "pro")
    billing_env.fail_fetch = True
    assert _post(client, _event("sub_TEST0001"), event_id="evt_api_2").status_code == 500


def test_webhook_rejects_huge_payload(client, billing_env):
    r = client.post("/webhooks/razorpay", content=b"x" * 1_000_001,
                    headers={"X-Razorpay-Signature": "x"})
    assert r.status_code == 413
