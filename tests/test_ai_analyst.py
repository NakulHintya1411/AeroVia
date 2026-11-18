from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from config.plans import get_plan
from config.settings import get_settings
from services import ai_analyst, usage


class FakeClient:
    def __init__(self, stop_reason="end_turn", text="RASK looks healthy."):
        self.calls = []
        self.stop_reason = stop_reason
        self.text = text
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            model=kwargs["model"],
            stop_reason=self.stop_reason,
            usage=SimpleNamespace(input_tokens=120, output_tokens=45),
            content=[SimpleNamespace(type="thinking", thinking=""),
                     SimpleNamespace(type="text", text=self.text)],
        )


MSGS = [{"role": "user", "content": "How is DEL-BOM doing?"}]


def test_ask_returns_text_and_records_usage(org_user):
    fake = FakeClient()
    reply = ai_analyst.ask(org_user.org_id, org_user.user_id, MSGS, "Route: DEL→BOM",
                           client_factory=lambda: fake)
    assert reply == "RASK looks healthy."
    assert usage.ai_quota(org_user.org_id).used == 1

    call = fake.calls[0]
    assert call["model"] == "claude-opus-5-5"
    assert call["output_config"] == {"effort": "medium"}
    assert call["fallbacks"] == "default"
    assert ai_analyst.FALLBACK_BETA in call["betas"]
    assert "thinking" not in call
    assert "DEL→BOM" in call["system"]
    assert call["messages"] == MSGS


def test_model_and_effort_come_from_settings(org_user, monkeypatch):
    monkeypatch.setenv("CLAUDE_MODEL", "claude-sonnet-5-5")
    monkeypatch.setenv("CLAUDE_EFFORT", "low")
    get_settings.cache_clear()
    fake = FakeClient()
    ai_analyst.ask(org_user.org_id, org_user.user_id, MSGS, client_factory=lambda: fake)
    assert fake.calls[0]["model"] == "claude-sonnet-5-5"
    assert fake.calls[0]["output_config"] == {"effort": "low"}


def test_quota_blocks_call_before_hitting_api(org_user):
    limit = get_plan("free").ai_messages_per_month
    for _ in range(limit):
        usage.record(org_user.org_id, org_user.user_id, usage.AI_MESSAGE)
    fake = FakeClient()
    with pytest.raises(ai_analyst.QuotaExceeded):
        ai_analyst.ask(org_user.org_id, org_user.user_id, MSGS, client_factory=lambda: fake)
    assert fake.calls == []


def test_quota_is_per_organisation(org_user):
    from services import accounts

    other = accounts.register("b@example.com", "B", "long-enough-pw", "Other")
    for _ in range(5):
        usage.record(org_user.org_id, org_user.user_id, usage.AI_MESSAGE)
    assert usage.ai_quota(org_user.org_id).used == 5
    assert usage.ai_quota(other.org_id).used == 0


def test_not_configured_without_key(org_user, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(ai_analyst.AnalystNotConfigured):
        ai_analyst.ask(org_user.org_id, org_user.user_id, MSGS, client_factory=FakeClient)


def test_refusal_gives_friendly_message(org_user):
    fake = FakeClient(stop_reason="refusal", text="")
    reply = ai_analyst.ask(org_user.org_id, org_user.user_id, MSGS, client_factory=lambda: fake)
    assert "can't help" in reply


def test_month_start():
    assert usage.month_start(datetime(2026, 11, 19, 15, 30, tzinfo=timezone.utc)) == \
        datetime(2026, 11, 1, tzinfo=timezone.utc)
