from decimal import Decimal

from pydantic import BaseModel


class ParticipantBalance(BaseModel):
    participant_id: str
    name: str
    balance: Decimal
    currency: str


class SettlementRead(BaseModel):
    from_participant_id: str
    from_name: str
    to_participant_id: str
    to_name: str
    amount: Decimal
    currency: str


class GroupSettlementSummary(BaseModel):
    balances: list[ParticipantBalance]
    settlements: list[SettlementRead]
