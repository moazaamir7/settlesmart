from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Header, HTTPException, Response, UploadFile, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_db
from app.models.user import AdminUser
from app.schemas.expense import ExpenseCreate, ExpenseRead
from app.schemas.group import (
    GroupCreate,
    GroupInviteRead,
    GuestSessionRead,
    GroupMessageCreate,
    GroupMessageRead,
    GroupRead,
    GroupUpdate,
    InvitePreview,
    ParticipantCreate,
    ParticipantRead,
)
from app.schemas.settlement import GroupSettlementSummary
from app.services.auth_service import AuthService
from app.services.auth_service import AccessIdentity
from app.services.expense_service import ExpenseService
from app.services.group_service import GroupService
from app.services.settlement_service import SettlementService
from app.services.realtime import realtime_manager

router = APIRouter(prefix="/groups", tags=["groups"])
UPLOAD_DIR = Path("/app/uploads")
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def get_current_admin(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AdminUser:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    return AuthService(db).get_admin_by_token(token)


def get_current_identity(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AccessIdentity:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    return AuthService(db).get_identity(token)


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> GroupRead:
    return GroupService(db).create_group(payload, admin)


@router.get("", response_model=list[GroupRead])
def list_groups(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> list[GroupRead]:
    return GroupService(db).list_groups(admin)


@router.get("/{group_id}", response_model=GroupRead)
def get_group(
    group_id: str,
    db: Session = Depends(get_db),
    identity: AccessIdentity = Depends(get_current_identity),
) -> GroupRead:
    return GroupService(db).require_access(group_id, identity)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> Response:
    GroupService(db).delete_group(group_id, admin)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{group_id}", response_model=GroupRead)
def update_group(
    group_id: str,
    payload: GroupUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> GroupRead:
    return GroupService(db).update_group(group_id, payload, admin)


@router.post("/{group_id}/participants", response_model=ParticipantRead, status_code=status.HTTP_201_CREATED)
def add_participant(
    group_id: str,
    payload: ParticipantCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> ParticipantRead:
    return GroupService(db).add_participant(group_id, payload, admin)


@router.delete("/{group_id}/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_participant(
    group_id: str,
    participant_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> Response:
    GroupService(db).remove_participant(group_id, participant_id, admin)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{group_id}/invites", response_model=GroupInviteRead, status_code=status.HTTP_201_CREATED)
def create_invite(
    group_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> GroupInviteRead:
    return GroupService(db).create_invite(group_id, admin)


@router.get("/invites/{token}", response_model=InvitePreview)
def get_invite(token: str, db: Session = Depends(get_db)) -> InvitePreview:
    invite = GroupService(db).get_invite_or_404(token)
    return InvitePreview(token=invite.token, group=invite.group)


@router.post("/invites/{token}/join", response_model=GuestSessionRead, status_code=status.HTTP_201_CREATED)
def join_invite(
    token: str,
    payload: ParticipantCreate,
    db: Session = Depends(get_db),
) -> GuestSessionRead:
    guest_token, participant = GroupService(db).join_with_invite(token, payload)
    return GuestSessionRead(token=guest_token, group_id=participant.group_id, participant=participant)


@router.get("/{group_id}/messages", response_model=list[GroupMessageRead])
def list_messages(
    group_id: str,
    db: Session = Depends(get_db),
    identity: AccessIdentity = Depends(get_current_identity),
) -> list[GroupMessageRead]:
    return GroupService(db).list_messages(group_id, identity)


@router.post("/{group_id}/messages", response_model=GroupMessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(
    group_id: str,
    payload: GroupMessageCreate,
    db: Session = Depends(get_db),
    identity: AccessIdentity = Depends(get_current_identity),
) -> GroupMessageRead:
    message = GroupService(db).create_message(group_id, payload, identity)
    result = GroupMessageRead.model_validate(message)
    await realtime_manager.broadcast_message(group_id, result)
    return result


@router.post("/{group_id}/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def add_expense(
    group_id: str,
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> ExpenseRead:
    expense = ExpenseService(db).add_expense(group_id, payload, admin)
    return ExpenseRead.from_model(expense)


@router.get("/{group_id}/expenses", response_model=list[ExpenseRead])
def list_expenses(
    group_id: str,
    db: Session = Depends(get_db),
    identity: AccessIdentity = Depends(get_current_identity),
) -> list[ExpenseRead]:
    GroupService(db).require_access(group_id, identity)
    return [ExpenseRead.from_model(expense) for expense in ExpenseService(db).list_group_expenses(group_id)]


@router.get("/{group_id}/settlements", response_model=GroupSettlementSummary)
def get_settlements(
    group_id: str,
    db: Session = Depends(get_db),
    identity: AccessIdentity = Depends(get_current_identity),
) -> GroupSettlementSummary:
    GroupService(db).require_access(group_id, identity)
    return SettlementService(db).summarize_group(group_id)


@router.post("/{group_id}/image", response_model=GroupRead)
async def upload_group_image(
    group_id: str,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> GroupRead:
    extension = ALLOWED_IMAGE_TYPES.get(image.content_type or "")
    if extension is None:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Use a JPG, PNG, or WebP image.")
    content = await image.read(MAX_IMAGE_BYTES + 1)
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image must be 5 MB or smaller.")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{group_id}-{uuid4().hex}{extension}"
    (UPLOAD_DIR / filename).write_bytes(content)
    return GroupService(db).update_group_image(group_id, f"/uploads/{filename}", admin)


@router.websocket("/{group_id}/ws")
async def group_websocket(websocket: WebSocket, group_id: str, token: str) -> None:
    with SessionLocal() as db:
        try:
            identity = AuthService(db).get_identity(token)
            GroupService(db).require_access(group_id, identity)
        except HTTPException:
            await websocket.close(code=4401)
            return
    await realtime_manager.connect(group_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        realtime_manager.disconnect(group_id, websocket)
