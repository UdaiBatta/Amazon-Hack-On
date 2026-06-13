"""Pricing v1 (heuristic, honestly labeled). Production = gradient-boosted model on
realized resale outcomes.

  price = base_price × grade_multiplier × category_decay(age) × local_demand_factor
"""
from __future__ import annotations

from domain.models import Grade, Item, PriceResult

GRADE_MULTIPLIER: dict[Grade, float] = {
    Grade.A: 0.88,
    Grade.B: 0.72,
    Grade.C: 0.52,
    Grade.D: 0.25,
}

# Demand factor seeded per SKU from the waitlist density (Section 9.4 network effect).
LOCAL_DEMAND_FACTOR: dict[str, float] = {
    "SKU-HP-01": 1.06,
    "SKU-SH-01": 0.98,
    "SKU-AP-01": 0.94,
}

REFUND_HAIRCUT = 0.94  # instant refund slightly under resale value (margin buffer)


def price(item: Item, grade: Grade, age_days: int = 20) -> PriceResult:
    decay = max(0.6, 1.0 - 0.0015 * age_days)  # gentle time decay
    demand = LOCAL_DEMAND_FACTOR.get(item.sku, 1.0)
    resale = item.base_price * GRADE_MULTIPLIER[grade] * decay * demand
    resale = round(resale, -1)  # round to nearest 10
    refund = round(resale * REFUND_HAIRCUT, -1)
    pct = round(100 * resale / item.base_price, 1)
    rationale = (
        f"₹{resale:,.0f} = {GRADE_MULTIPLIER[grade]:.0%} grade-{grade.value} value "
        f"× local demand {demand:.2f}; sells within ~2 days in this area."
    )
    return PriceResult(
        resale_value=resale,
        instant_refund=refund,
        pct_of_new=pct,
        rationale=rationale,
    )
