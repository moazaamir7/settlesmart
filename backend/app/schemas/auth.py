from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AdminSignup(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=10, max_length=120)
    display_name: str = Field(min_length=1, max_length=120)
    settlement_contact: str = Field(default="", max_length=160)


class AdminLogin(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=120)


class AdminRead(ORMModel):
    id: str
    email: str
    display_name: str
    settlement_contact: str
    created_at: datetime


class AuthSession(BaseModel):
    token: str
    admin: AdminRead
