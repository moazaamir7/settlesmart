from app.algorithms.debt_settlement import calculate_balances, optimize_settlements


def test_calculate_balances_from_expenses() -> None:
    balances = calculate_balances(
        [
            ("adam", 12000, {"adam": 3000, "omar": 3000, "ali": 3000, "sara": 3000}),
            ("ali", 4000, {"adam": 2000, "ali": 2000}),
        ]
    )

    assert balances == {
        "adam": 7000,
        "omar": -3000,
        "ali": -1000,
        "sara": -3000,
    }


def test_optimize_settlements_minimizes_transfers_reasonably() -> None:
    payments = optimize_settlements(
        {
            "adam": -3500,
            "omar": -900,
            "ali": 2600,
            "sara": 1800,
        }
    )

    assert [(p.from_participant_id, p.to_participant_id, p.amount_cents) for p in payments] == [
        ("adam", "ali", 2600),
        ("adam", "sara", 900),
        ("omar", "sara", 900),
    ]
    assert len(payments) == 3
