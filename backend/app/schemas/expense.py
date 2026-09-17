from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.algorithms.money import cents_to_decimal
from app.models.expense import Expense
from app.schemas.common import ORMModel
from app.schemas.group import ParticipantRead


EXPENSE_CATEGORIES = {
    "Restaurant",
    "Groceries",
    "Transportation",
    "Accommodation",
    "Entertainment",
    "Shopping",
    "Utilities",
    "Tickets",
    "Other",
}


class ExpenseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category: str = "Other"
    payer_id: str = Field(min_length=1)
    participant_ids: list[str] = Field(min_length=1)
    subtotal: Decimal = Field(gt=0, max_digits=12, decimal_places=2, allow_inf_nan=False)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100, max_digits=5, decimal_places=2, allow_inf_nan=False)
    tax_amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2, allow_inf_nan=False)
    tip_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100, max_digits=5, decimal_places=2, allow_inf_nan=False)
    tip_amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2, allow_inf_nan=False)
    fees: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2, allow_inf_nan=False)
    discounts: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2, allow_inf_nan=False)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Expense name is required.")
        return value

    @model_validator(mode="after")
    def validate_category_and_unique_participants(self) -> "ExpenseCreate":
        if self.category not in EXPENSE_CATEGORIES:
            raise ValueError(f"Unsupported category: {self.category}")
        if len(set(self.participant_ids)) != len(self.participant_ids):
            raise ValueError("Participants must be unique.")
        tax = self.tax_amount if self.tax_amount is not None else self.subtotal * self.tax_rate / Decimal("100")
        tip = self.tip_amount if self.tip_amount is not None else self.subtotal * self.tip_rate / Decimal("100")
        if self.discounts > self.subtotal + tax + tip + self.fees:
            raise ValueError("Discount cannot be greater than the expense total.")
        return self


class ExpenseParticipantRead(ORMModel):
    participant: ParticipantRead
    share: Decimal


class ExpenseRead(ORMModel):
    id: str
    group_id: str
    name: str
    category: str
    payer: ParticipantRead
    subtotal: Decimal
    tax: Decimal
    tip: Decimal
    fees: Decimal
    discounts: Decimal
    total: Decimal
    currency: str
    split_method: str
    source: str
    created_at: datetime
    participants: list[ExpenseParticipantRead]

    @classmethod
    def from_model(cls, expense: Expense) -> "ExpenseRead":
        return cls(
            id=expense.id,
            group_id=expense.group_id,
            name=expense.name,
            category=expense.category,
            payer=expense.payer,
            subtotal=cents_to_decimal(expense.subtotal_cents),
            tax=cents_to_decimal(expense.tax_cents),
            tip=cents_to_decimal(expense.tip_cents),
            fees=cents_to_decimal(expense.fees_cents),
            discounts=cents_to_decimal(expense.discounts_cents),
            total=cents_to_decimal(expense.total_cents),
            currency=expense.currency,
            split_method=expense.split_method,
            source=expense.source,
            created_at=expense.created_at,
            participants=[
                ExpenseParticipantRead(
                    participant=participant.participant,
                    share=cents_to_decimal(participant.share_cents),
                )
                for participant in expense.participants
            ],
        )
