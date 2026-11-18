"""Users, organisations, and sign-in.

Passwords are bcrypt-hashed. Repeated failed sign-ins lock the account for a
short period to slow down password guessing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from sqlalchemy import func, select

from config.plans import DEFAULT_PLAN
from config.settings import get_settings
from db import session_scope
from db.models import Membership, Organization, User, utcnow
from services import billing

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_BYTES = 72  # bcrypt only uses the first 72 bytes
MAX_FAILED_LOGINS = 5
LOCKOUT_MINUTES = 15

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Checked when the email is unknown so that response time doesn't reveal
# which addresses have accounts.
_DUMMY_HASH = bcrypt.hashpw(b"aerovia-timing-equaliser", bcrypt.gensalt()).decode()


class AccountError(ValueError):
    """A problem the user can fix; the message is safe to show them."""


@dataclass(frozen=True)
class SessionUser:
    """What the app keeps about the signed-in user. Plain data, no ORM objects."""

    user_id: int
    email: str
    name: str
    org_id: int
    org_name: str
    role: str
    plan: str


def normalise_email(email: str) -> str:
    return (email or "").strip().lower()


def validate_email(email: str) -> str:
    email = normalise_email(email)
    if not _EMAIL_RE.match(email) or len(email) > 255:
        raise AccountError("Enter a valid email address.")
    return email


def validate_password(password: str) -> None:
    if len(password or "") < MIN_PASSWORD_LENGTH:
        raise AccountError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise AccountError("Password is too long (maximum 72 bytes).")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def _check(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8")[:MAX_PASSWORD_BYTES], password_hash.encode())
    except ValueError:
        return False


def _as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    # SQLite hands back naive datetimes; everything we store is UTC.
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def user_count() -> int:
    with session_scope() as s:
        return s.scalar(select(func.count(User.id))) or 0


def signup_open() -> bool:
    """Sign-up is open if enabled in settings, or if no account exists yet."""
    return get_settings().allow_signup or user_count() == 0


def register(email: str, name: str, password: str, org_name: str) -> SessionUser:
    """Create a user plus a new organisation that they own."""
    if not signup_open():
        raise AccountError("Sign-up is currently invite-only.")
    email = validate_email(email)
    name = (name or "").strip()
    org_name = (org_name or "").strip()
    if not name:
        raise AccountError("Enter your name.")
    if not org_name:
        raise AccountError("Enter your organisation's name.")
    if len(name) > 120 or len(org_name) > 120:
        raise AccountError("Name and organisation must be 120 characters or fewer.")
    validate_password(password)

    with session_scope() as s:
        if s.scalar(select(User.id).where(User.email == email)) is not None:
            raise AccountError("An account with this email already exists.")
        org = Organization(name=org_name, plan=DEFAULT_PLAN,
                           trial_ends_at=billing.trial_end_for_new_org())
        user = User(email=email, name=name, password_hash=hash_password(password))
        s.add_all([org, user])
        s.flush()
        s.add(Membership(user_id=user.id, org_id=org.id, role="owner"))
        s.flush()
        return SessionUser(user.id, user.email, user.name, org.id, org.name, "owner",
                           billing.effective_plan_key(s, org))


def authenticate(email: str, password: str) -> SessionUser:
    """Return the signed-in user, or raise AccountError with a safe message."""
    email = normalise_email(email)
    generic = AccountError("Incorrect email or password.")
    now = utcnow()

    with session_scope() as s:
        user = s.scalar(select(User).where(User.email == email))
        if user is None:
            _check(password or "", _DUMMY_HASH)
            raise generic

        locked_until = _as_utc(user.locked_until)
        if locked_until and locked_until > now:
            minutes = max(1, int((locked_until - now).total_seconds() // 60) + 1)
            raise AccountError(f"Too many failed attempts. Try again in {minutes} minute(s).")

        if not user.is_active or not _check(password or "", user.password_hash):
            user.failed_login_count = (user.failed_login_count or 0) + 1
            if user.failed_login_count >= MAX_FAILED_LOGINS:
                user.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
                user.failed_login_count = 0
            # Commit the counter even though we're about to fail.
            s.commit()
            raise generic

        membership = s.scalar(
            select(Membership).where(Membership.user_id == user.id).order_by(Membership.id)
        )
        if membership is None:
            raise AccountError("Your account isn't linked to an organisation. Contact support.")

        user.failed_login_count = 0
        user.locked_until = None
        user.last_login_at = now
        org = membership.organization
        return SessionUser(user.id, user.email, user.name, org.id, org.name, membership.role,
                           billing.effective_plan_key(s, org))


def refresh(user_id: int, org_id: int) -> Optional[SessionUser]:
    """Reload the session user (plan or role may have changed). None if access was removed."""
    with session_scope() as s:
        row = s.execute(
            select(User, Membership, Organization)
            .join(Membership, Membership.user_id == User.id)
            .join(Organization, Organization.id == Membership.org_id)
            .where(User.id == user_id, Organization.id == org_id, User.is_active.is_(True))
        ).first()
        if row is None:
            return None
        user, membership, org = row
        return SessionUser(user.id, user.email, user.name, org.id, org.name, membership.role,
                           billing.effective_plan_key(s, org))


def list_members(org_id: int) -> list[dict]:
    with session_scope() as s:
        rows = s.execute(
            select(User.name, User.email, Membership.role, Membership.created_at)
            .join(Membership, Membership.user_id == User.id)
            .where(Membership.org_id == org_id)
            .order_by(Membership.id)
        ).all()
        return [{"name": n, "email": e, "role": r, "joined": j} for n, e, r, j in rows]
