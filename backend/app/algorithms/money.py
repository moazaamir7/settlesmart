from decimal import Decimal, ROUND_HALF_UP


CENT = Decimal("0.01")


def decimal_to_cents(value: Decimal) -> int:
    return int((value.quantize(CENT, rounding=ROUND_HALF_UP) * 100).to_integral_value())


def cents_to_decimal(cents: int) -> Decimal:
    return (Decimal(cents) / Decimal(100)).quantize(CENT)


def allocate_cents(total_cents: int, weights: list[int]) -> list[int]:
    if not weights:
        raise ValueError("At least one weight is required.")
    if any(weight < 0 for weight in weights):
        raise ValueError("Weights cannot be negative.")

    weight_sum = sum(weights)
    if weight_sum <= 0:
        raise ValueError("At least one weight must be positive.")

    raw = [(total_cents * weight, index) for index, weight in enumerate(weights)]
    shares = [amount // weight_sum for amount, _ in raw]
    remainder = total_cents - sum(shares)

    ranked_remainders = sorted(
        ((amount % weight_sum, index) for amount, index in raw),
        reverse=True,
    )
    for _, index in ranked_remainders[:remainder]:
        shares[index] += 1

    return shares
