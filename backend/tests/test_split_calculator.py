from decimal import Decimal

import pytest

from app.algorithms.money import allocate_cents, cents_to_decimal, decimal_to_cents
from app.algorithms.split_calculator import EqualSplitInput, calculate_equal_split


def test_decimal_to_cents_rounds_half_up() -> None:
    assert decimal_to_cents(Decimal("10.005")) == 1001
    assert cents_to_decimal(1001) == Decimal("10.01")


def test_allocate_cents_distributes_remainder_deterministically() -> None:
    assert allocate_cents(100, [1, 1, 1]) == [33, 33, 34]


def test_equal_split_calculates_tax_tip_and_total() -> None:
    result = calculate_equal_split(
        EqualSplitInput(
            subtotal=Decimal("100.00"),
            tax_rate=Decimal("13"),
            tip_rate=Decimal("18"),
            participant_ids=("adam", "omar", "ali", "sara"),
        )
    )

    assert result.subtotal_cents == 10000
    assert result.tax_cents == 1300
    assert result.tip_cents == 1800
    assert result.total_cents == 13100
    assert result.shares_by_participant == {
        "adam": 3275,
        "omar": 3275,
        "ali": 3275,
        "sara": 3275,
    }


def test_equal_split_supports_manual_tax_and_tip_amounts() -> None:
    result = calculate_equal_split(
        EqualSplitInput(
            subtotal=Decimal("73.00"),
            tax_amount=Decimal("9.49"),
            tip_amount=Decimal("15.00"),
            participant_ids=("adam", "omar"),
        )
    )

    assert result.total_cents == 9749
    assert sum(result.shares_by_participant.values()) == 9749


def test_equal_split_rejects_empty_participants() -> None:
    with pytest.raises(ValueError, match="participant"):
        calculate_equal_split(EqualSplitInput(subtotal=Decimal("20.00")))
