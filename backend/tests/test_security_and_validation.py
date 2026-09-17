import pytest
from pydantic import ValidationError

from app.schemas.group import GroupCreate
from app.schemas.expense import ExpenseCreate
from app.services.auth_service import AuthService


def test_password_hash_round_trip_and_rejects_wrong_password() -> None:
    password_hash = AuthService.hash_password("StrongPassword123!")

    assert AuthService.verify_password("StrongPassword123!", password_hash)
    assert not AuthService.verify_password("wrong-password", password_hash)
    assert "StrongPassword123!" not in password_hash


@pytest.mark.parametrize("currency", ["CAD", "USD"])
def test_supported_group_currencies(currency: str) -> None:
    group = GroupCreate(name="Trip", currency=currency)

    assert group.currency == currency


@pytest.mark.parametrize("currency", ["EUR", "cad", "US", "USDD"])
def test_unsupported_group_currencies_are_rejected(currency: str) -> None:
    with pytest.raises(ValidationError):
        GroupCreate(name="Trip", currency=currency)


def valid_expense(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "Dinner",
        "category": "Restaurant",
        "payer_id": "payer",
        "participant_ids": ["payer"],
        "subtotal": "50.00",
        "tax_rate": "13",
        "tip_rate": "18",
        "fees": "0",
        "discounts": "0",
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("subtotal", "letters"),
        ("subtotal", "0"),
        ("tax_rate", "101"),
        ("tax_rate", "NaN"),
        ("tip_rate", "-1"),
        ("fees", "-0.01"),
    ],
)
def test_invalid_expense_numbers_are_rejected(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        ExpenseCreate(**valid_expense(**{field: value}))


def test_discount_cannot_make_expense_total_negative() -> None:
    with pytest.raises(ValidationError, match="Discount cannot be greater"):
        ExpenseCreate(**valid_expense(subtotal="10", tax_rate="0", tip_rate="0", discounts="10.01"))
