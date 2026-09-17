from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import AdminLogin, AdminRead, AdminSignup, AuthSession
from app.schemas.group import GuestSessionRead, ParticipantRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthSession)
def signup(payload: AdminSignup, db: Session = Depends(get_db)) -> AuthSession:
    token, admin = AuthService(db).signup(payload)
    return AuthSession(token=token, admin=AdminRead.model_validate(admin))


@router.post("/login", response_model=AuthSession)
def login(payload: AdminLogin, db: Session = Depends(get_db)) -> AuthSession:
    token, admin = AuthService(db).login(payload)
    return AuthSession(token=token, admin=AdminRead.model_validate(admin))


@router.get("/me", response_model=AdminRead)
def me(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AdminRead:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    admin = AuthService(db).get_admin_by_token(token)
    return AdminRead.model_validate(admin)


@router.get("/guest/me", response_model=GuestSessionRead)
def guest_me(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> GuestSessionRead:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    guest_session, participant = AuthService(db).get_guest_session(token)
    return GuestSessionRead(token=guest_session.token, group_id=guest_session.group_id, participant=ParticipantRead.model_validate(participant))


@router.delete("/session", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Response:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    AuthService(db).revoke_session(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
