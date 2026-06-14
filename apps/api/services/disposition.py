"""Disposition engine: rules decide the path, AI explains it (explainable routing).

  Grade A/B + nearby demand + resale > liquidation → DIRECT_RELAY
  Grade C                                          → LIQUIDATION
  Grade D / fraud-flag                             → RECYCLE / MANUAL_REVIEW

Relay is the best path, never the only path — it degrades gracefully.
"""
from __future__ import annotations

from ai.bedrock import ai
from fallbacks.cached import CACHED_DISPOSITION
from domain.models import (
    Disposition,
    DispositionResult,
    Grade,
    GradeResult,
    PriceResult,
    TrustScore,
)

LIQUIDATION_FLOOR = 900.0  # what a pallet liquidator would pay


def decide(
    grade: GradeResult,
    price: PriceResult,
    trust: TrustScore,
    nearby_demand: int,
    nearest_km: float | None,
) -> DispositionResult:
    if not trust.passed:
        return DispositionResult(
            path=Disposition.review,
            explanation=(
                "Trust screen failed — routed to human review with full evidence "
                "bundle. AI flags, humans accuse."
            ),
            price=price,
        )

    if grade.grade in (Grade.A, Grade.B) and nearby_demand > 0 and (
        price.resale_value > LIQUIDATION_FLOOR
    ):
        return DispositionResult(
            path=Disposition.relay,
            explanation=(
                f"Grade {grade.grade.value} + {nearby_demand} buyer(s) in demand "
                f"radius (nearest {nearest_km} km) + resale ₹{price.resale_value:,.0f} "
                f"> liquidation ₹{LIQUIDATION_FLOOR:,.0f} → DIRECT RELAY."
            ),
            price=price,
        )

    if grade.grade == Grade.C:
        return DispositionResult(
            path=Disposition.liquidate,
            explanation=(
                f"Grade C with limited local demand → liquidation channel "
                f"(₹{LIQUIDATION_FLOOR:,.0f} floor)."
            ),
            price=price,
        )

    return DispositionResult(
        path=Disposition.recycle,
        explanation="Grade D / low recoverable value → certified recycling.",
        price=price,
    )


async def explain(
    result: DispositionResult, facts: dict, sku: str | None = None
) -> tuple[DispositionResult, str]:
    """AI explains; the rule above already decided the path. Fallback ladder:

      rung 1 (live)  — Bedrock Haiku rephrase (AWS mode only)
      rung 2 (cache) — real captured Haiku output for this SKU (mock mode / live fail)
      rung 3 (rule)  — the deterministic explanation already on `result`

    Returns (result, source) with source ∈ live|cache|rule, explanation updated in place.
    """
    text, source = await ai.explain_disposition(
        path=result.path.value,
        base_explanation=result.explanation,
        facts=facts,
    )
    if source != "live" and sku and sku in CACHED_DISPOSITION:
        result.explanation = CACHED_DISPOSITION[sku]
        return result, "cache"
    result.explanation = text
    return result, source
