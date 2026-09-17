from datetime import datetime

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    currency: Literal["CAD", "USD"] = "CAD"
    settlement_contact: str = Field(default="", max_length=160)


class GroupUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    settlement_contact: str = Field(default="", max_length=160)


class ParticipantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ParticipantRead(ORMModel):
    id: str
    group_id: str
    name: str
    is_active: bool
    created_at: datetime


class GroupRead(ORMModel):
    id: str
    name: str
    currency: str
    admin_id: str | None = None
    settlement_contact: str = ""
    image_url: str | None = None
    owner_participant_id: str | None = None
    created_at: datetime
    participants: list[ParticipantRead] = []


class GroupInviteRead(ORMModel):
    id: str
    group_id: str
    token: str
    created_at: datetime


class InviteGroupPreview(ORMModel):
    id: str
    name: str
    currency: str
    image_url: str | None = None


class InvitePreview(BaseModel):
    token: str
    group: InviteGroupPreview


class GroupMessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class GroupMessageRead(ORMModel):
    id: str
    group_id: str
    sender_name: str
    body: str
    created_at: datetime


class GuestSessionRead(BaseModel):
    token: str
    group_id: str
    participant: ParticipantRead
