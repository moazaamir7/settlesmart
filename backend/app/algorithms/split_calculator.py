from dataclasses import dataclass
from decimal import Decimal

from app.algorithms.money import allocate_cents, decimal_to_cents


@dataclass(frozen=True)
class EqualSplitInput:
    subtotal: Decimal
    tax_rate: Decimal = Decimal("0")
    tax_amount: Decimal | None = None
    tip_rate: Decimal = Decimal("0")
    tip_amount: Decimal | None = None
    fees: Decimal = Decimal("0")
    discounts: Decimal = Decimal("0")
    participant_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EqualSplitResult:
    subtotal_cents: int
    tax_cents: int
    tip_cents: int
    fees_cents: int
    discounts_cents: int
    total_cents: int
    shares_by_participant: dict[str, int]


def calculate_equal_split(payload: EqualSplitInput) -> EqualSplitResult:
    if payload.subtotal < 0:
        raise ValueError("Subtotal cannot be negative.")
    if payload.fees < 0 or payload.discounts < 0:
        raise ValueError("Fees and discounts cannot be negative.")
    if not payload.participant_ids:
        raise ValueError("At least one participant is required.")

    subtotal_cents = decimal_to_cents(payload.subtotal)
    tax_cents = (
        decimal_to_cents(payload.tax_amount)
        if payload.tax_amount is not None
        else decimal_to_cents(payload.subtotal * payload.tax_rate / Decimal("100"))
    )
    tip_cents = (
        decimal_to_cents(payload.tip_amount)
        if payload.tip_amount is not None
        else decimal_to_cents(payload.subtotal * payload.tip_rate / Decimal("100"))
    )
    fees_cents = decimal_to_cents(payload.fees)
    discounts_cents = decimal_to_cents(payload.discounts)
    total_cents = subtotal_cents + tax_cents + tip_cents + fees_cents - discounts_cents

    if total_cents < 0:
        raise ValueError("Total cannot be negative.")

    shares = allocate_cents(total_cents, [1 for _ in payload.participant_ids])
    return EqualSplitResult(
        subtotal_cents=subtotal_cents,
        tax_cents=tax_cents,
        tip_cents=tip_cents,
        fees_cents=fees_cents,
        discounts_cents=discounts_cents,
        total_cents=total_cents,
        shares_by_participant=dict(zip(payload.participant_ids, shares, strict=True)),
    )
