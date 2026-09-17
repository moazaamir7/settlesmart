import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.group import Participant
from app.models.user import AdminSession, AdminUser, GuestSession
from app.schemas.auth import AdminLogin, AdminSignup


@dataclass(frozen=True)
class AccessIdentity:
    token: str
    role: str
    name: str
    admin: AdminUser | None = None
    group_id: str | None = None
    participant_id: str | None = None


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def signup(self, payload: AdminSignup) -> tuple[str, AdminUser]:
        email = self.normalize_email(payload.email)
        if self.get_admin_by_email(email) is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An account with that email already exists.")

        admin = AdminUser(
            email=email,
            password_hash=self.hash_password(payload.password),
            display_name=payload.display_name.strip(),
            settlement_contact=payload.settlement_contact.strip(),
        )
        self.db.add(admin)
        self.db.flush()
        token = self.create_session(admin.id)
        self.db.commit()
        self.db.refresh(admin)
        return token, admin

    def login(self, payload: AdminLogin) -> tuple[str, AdminUser]:
        admin = self.get_admin_by_email(self.normalize_email(payload.email))
        if admin is None or not self.verify_password(payload.password, admin.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect.")
        token = self.create_session(admin.id)
        self.db.commit()
        self.db.refresh(admin)
        return token, admin

    def get_admin_by_token(self, token: str | None) -> AdminUser:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Log in as an admin first.")
        session = self.db.scalar(
            select(AdminSession)
            .where(AdminSession.token == token)
            .join(AdminSession.admin)
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your admin session has expired.")
        if self.is_expired(session.created_at, days=30):
            self.db.delete(session)
            self.db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your admin session has expired.")
        return session.admin

    def create_guest_session(self, participant: Participant) -> str:
        token = token_urlsafe(36)
        self.db.add(GuestSession(group_id=participant.group_id, participant_id=participant.id, token=token))
        self.db.commit()
        return token

    def get_guest_session(self, token: str | None) -> tuple[GuestSession, Participant]:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Join the group with an invite first.")
        guest_session = self.db.scalar(select(GuestSession).where(GuestSession.token == token))
        if guest_session is None or self.is_expired(guest_session.created_at, days=7):
            if guest_session is not None:
                self.db.delete(guest_session)
                self.db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your guest session has expired.")
        participant = self.db.scalar(
            select(Participant).where(
                Participant.id == guest_session.participant_id,
                Participant.group_id == guest_session.group_id,
                Participant.is_active.is_(True),
            )
        )
        if participant is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This guest session is no longer active.")
        return guest_session, participant

    def get_identity(self, token: str | None) -> AccessIdentity:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required.")
        admin_session = self.db.scalar(select(AdminSession).where(AdminSession.token == token))
        if admin_session is not None:
            admin = self.get_admin_by_token(token)
            return AccessIdentity(token=token, role="admin", name=admin.display_name, admin=admin)
        guest_session, participant = self.get_guest_session(token)
        return AccessIdentity(
            token=token,
            role="guest",
            name=participant.name,
            group_id=guest_session.group_id,
            participant_id=participant.id,
        )

    def revoke_session(self, token: str | None) -> None:
        if not token:
            return
        session = self.db.scalar(select(AdminSession).where(AdminSession.token == token))
        if session is None:
            session = self.db.scalar(select(GuestSession).where(GuestSession.token == token))
        if session is not None:
            self.db.delete(session)
            self.db.commit()

    def create_session(self, admin_id: str) -> str:
        token = token_urlsafe(36)
        self.db.add(AdminSession(admin_id=admin_id, token=token))
        return token

    def get_admin_by_email(self, email: str) -> AdminUser | None:
        return self.db.scalar(select(AdminUser).where(AdminUser.email == email))

    @staticmethod
    def is_expired(created_at: datetime, days: int) -> bool:
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return created_at < datetime.now(timezone.utc) - timedelta(days=days)

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def hash_password(password: str) -> str:
        salt = uuid4().hex
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
        return f"pbkdf2_sha256${salt}${digest.hex()}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            algorithm, salt, expected = password_hash.split("$", 2)
        except ValueError:
            return False
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
        return hmac.compare_digest(digest.hex(), expected)
