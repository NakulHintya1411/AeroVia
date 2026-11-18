import pytest

from config.settings import get_settings
from services import accounts
from services.accounts import AccountError


def test_register_creates_owner_of_new_org(db):
    u = accounts.register("  Asha@Example.COM ", "Asha", "long-enough-pw", "Route Dev")
    assert u.email == "asha@example.com"
    assert u.role == "owner"
    assert u.plan == "free"
    assert u.org_name == "Route Dev"
    members = accounts.list_members(u.org_id)
    assert [m["email"] for m in members] == ["asha@example.com"]


def test_password_is_not_stored_in_plain_text(db):
    from sqlalchemy import select

    from db import session_scope
    from db.models import User

    accounts.register("a@example.com", "A", "long-enough-pw", "Org")
    with session_scope() as s:
        stored = s.scalar(select(User.password_hash))
    assert "long-enough-pw" not in stored
    assert stored.startswith("$2")


@pytest.mark.parametrize("email,name,pw,org,msg", [
    ("not-an-email", "A", "long-enough-pw", "Org", "valid email"),
    ("a@example.com", "", "long-enough-pw", "Org", "your name"),
    ("a@example.com", "A", "long-enough-pw", "", "organisation"),
    ("a@example.com", "A", "short", "Org", "at least"),
    ("a@example.com", "A", "x" * 73, "Org", "too long"),
])
def test_register_validation(db, email, name, pw, org, msg):
    with pytest.raises(AccountError, match=msg):
        accounts.register(email, name, pw, org)


def test_duplicate_email_rejected_case_insensitively(db):
    accounts.register("a@example.com", "A", "long-enough-pw", "Org")
    with pytest.raises(AccountError, match="already exists"):
        accounts.register("A@EXAMPLE.com", "B", "long-enough-pw", "Org 2")


def test_authenticate_success_and_failure(org_user):
    u = accounts.authenticate("OWNER@example.com", "correct-horse-1")
    assert u.user_id == org_user.user_id
    with pytest.raises(AccountError, match="Incorrect email or password"):
        accounts.authenticate("owner@example.com", "wrong-password")
    with pytest.raises(AccountError, match="Incorrect email or password"):
        accounts.authenticate("nobody@example.com", "whatever-123")


def test_account_locks_after_repeated_failures(org_user):
    for _ in range(accounts.MAX_FAILED_LOGINS):
        with pytest.raises(AccountError, match="Incorrect"):
            accounts.authenticate("owner@example.com", "wrong-password")
    # Even the right password is refused while locked.
    with pytest.raises(AccountError, match="Too many failed attempts"):
        accounts.authenticate("owner@example.com", "correct-horse-1")


def test_successful_login_resets_failure_count(org_user):
    for _ in range(accounts.MAX_FAILED_LOGINS - 1):
        with pytest.raises(AccountError):
            accounts.authenticate("owner@example.com", "wrong-password")
    accounts.authenticate("owner@example.com", "correct-horse-1")
    for _ in range(accounts.MAX_FAILED_LOGINS - 1):
        with pytest.raises(AccountError, match="Incorrect"):
            accounts.authenticate("owner@example.com", "wrong-password")


def test_first_account_allowed_even_when_signup_disabled(db, monkeypatch):
    monkeypatch.setenv("AEROVIA_ALLOW_SIGNUP", "false")
    get_settings.cache_clear()
    accounts.register("first@example.com", "First", "long-enough-pw", "Org")
    with pytest.raises(AccountError, match="invite-only"):
        accounts.register("second@example.com", "Second", "long-enough-pw", "Org 2")


def test_refresh_returns_none_for_unknown_membership(org_user):
    assert accounts.refresh(org_user.user_id, org_user.org_id) == org_user
    assert accounts.refresh(org_user.user_id, org_user.org_id + 999) is None
