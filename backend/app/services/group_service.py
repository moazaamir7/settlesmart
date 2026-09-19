from secrets import token_urlsafe
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.group import Group, GroupInvite, GroupMessage, Participant
from app.core.config import get_settings
from app.repositories.group_repository import GroupRepository
from app.models.user import AdminUser
from app.schemas.group import GroupCreate, GroupMessageCreate, GroupUpdate, ParticipantCreate
from app.services.auth_service import AccessIdentity, AuthService


class GroupService:
    def __init__(self, db: Session) -> None:
        self.repository = GroupRepository(db)

    def create_group(self, payload: GroupCreate, admin: AdminUser) -> Group:
        group = self.repository.create_group(
            payload.name,
            payload.currency,
            admin.id,
            payload.settlement_contact.strip() or admin.settlement_contact,
        )
        self.repository.add_participant(group.id, admin.display_name)
        return self.get_group_or_404(group.id)

    def list_groups(self, admin: AdminUser) -> list[Group]:
        return self.repository.list_groups(admin.id)

    def get_group_or_404(self, group_id: str) -> Group:
        group = self.repository.get_group(group_id)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")
        return group

    def require_admin(self, group_id: str, admin: AdminUser) -> Group:
        group = self.get_group_or_404(group_id)
        if group.admin_id != admin.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the group admin can do that.",
            )
        return group

    def update_group(self, group_id: str, payload: GroupUpdate, admin: AdminUser) -> Group:
        group = self.require_admin(group_id, admin)
        return self.repository.update_group(group, payload.name.strip(), payload.settlement_contact.strip())

    def delete_group(self, group_id: str, admin: AdminUser) -> None:
        group = self.require_admin(group_id, admin)
        image_path = self.upload_path(group.image_url)
        self.repository.delete_group(group_id)
        if image_path is not None:
            image_path.unlink(missing_ok=True)

    def add_participant(self, group_id: str, payload: ParticipantCreate, admin: AdminUser | None = None) -> Participant:
        group = self.get_group_or_404(group_id)
        if group.owner_participant_id is not None and admin is not None:
            self.require_admin(group_id, admin)
        elif group.owner_participant_id is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the group admin can do that.")
        return self.repository.add_participant(group_id, payload.name)

    def create_invite(self, group_id: str, admin: AdminUser) -> GroupInvite:
        self.require_admin(group_id, admin)
        return self.repository.create_invite(group_id, token_urlsafe(24))

    def get_invite_or_404(self, token: str) -> GroupInvite:
        invite = self.repository.get_invite_by_token(token)
        if invite is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite link not found.")
        return invite

    def join_with_invite(self, token: str, payload: ParticipantCreate) -> tuple[str, Participant]:
        invite = self.get_invite_or_404(token)
        participant = self.repository.add_participant(invite.group_id, payload.name)
        guest_token = AuthService(self.repository.db).create_guest_session(participant)
        return guest_token, participant

    def create_message(self, group_id: str, payload: GroupMessageCreate, identity: AccessIdentity) -> GroupMessage:
        self.require_access(group_id, identity)
        return self.repository.create_message(group_id, identity.name, payload.body.strip())

    def list_messages(self, group_id: str, identity: AccessIdentity) -> list[GroupMessage]:
        self.require_access(group_id, identity)
        return self.repository.list_messages(group_id)

    def require_access(self, group_id: str, identity: AccessIdentity) -> Group:
        group = self.get_group_or_404(group_id)
        if identity.role == "admin" and identity.admin and group.admin_id == identity.admin.id:
            return group
        if identity.role == "guest" and identity.group_id == group_id:
            return group
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this group.")

    def update_group_image(self, group_id: str, image_url: str, admin: AdminUser) -> Group:
        group = self.require_admin(group_id, admin)
        previous_path = self.upload_path(group.image_url)
        updated = self.repository.update_group_image(group, image_url)
        if previous_path is not None:
            previous_path.unlink(missing_ok=True)
        return updated

    @staticmethod
    def upload_path(image_url: str | None) -> Path | None:
        if not image_url or not image_url.startswith("/uploads/"):
            return None
        return get_settings().upload_path / Path(image_url).name

    def remove_participant(self, group_id: str, participant_id: str, admin: AdminUser) -> None:
        self.require_admin(group_id, admin)
        participant = self.repository.get_participant(group_id, participant_id)
        if participant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found.")
        group = self.get_group_or_404(group_id)
        if group.owner_participant_id == participant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The original group creator cannot be removed.",
            )
        self.repository.remove_participant(participant)
