"""Condition grading: a deterministic, defensible rubric over AI-extracted defects.

This is the "rules decide" half of the philosophy. The rubric lives in config here
(not in the prompt) so grades are consistent and auditable. Claude only writes the
human-readable rationale.
"""
from __future__ import annotations

from ai.schemas import Defect, DefectExtraction, Severity
from domain.models import Grade, GradeResult

# Severity penalty weights (the rubric). Tunable, versioned config.
SEVERITY_PENALTY: dict[Severity, float] = {
    Severity.cosmetic: 3.0,
    Severity.minor: 8.0,
    Severity.moderate: 18.0,
    Severity.major: 40.0,
}
FUNCTION_PENALTY = 25.0  # extra hit if a defect affects function

# Grade bands over a 0–100 condition score (100 = pristine).
BANDS: list[tuple[float, Grade]] = [
    (85.0, Grade.A),
    (65.0, Grade.B),
    (40.0, Grade.C),
    (0.0, Grade.D),
]


def _rationale(grade: Grade, defects: list[Defect], notes: str) -> str:
    if not defects:
        return f"Grade {grade.value}: no defects detected. {notes}".strip()
    worst = max(defects, key=lambda d: SEVERITY_PENALTY[d.severity])
    return (
        f"Grade {grade.value}: {len(defects)} defect(s) noted, "
        f"most significant a {worst.severity.value} {worst.type} on the "
        f"{worst.location}. {notes}"
    ).strip()


def grade(extraction: DefectExtraction) -> GradeResult:
    score = 100.0
    for d in extraction.defects:
        penalty = SEVERITY_PENALTY[d.severity]
        if d.affects_function:
            penalty += FUNCTION_PENALTY
        score -= penalty
    score = max(0.0, round(score, 1))

    letter = next(g for threshold, g in BANDS if score >= threshold)

    # Confidence = mean defect confidence blended with product-match confidence.
    if extraction.defects:
        mean_def_conf = sum(d.confidence for d in extraction.defects) / len(
            extraction.defects
        )
    else:
        mean_def_conf = 0.95
    confidence = round(
        0.5 * mean_def_conf + 0.5 * extraction.product_match.confidence, 3
    )

    return GradeResult(
        grade=letter,
        score=score,
        confidence=confidence,
        rationale=_rationale(letter, extraction.defects, extraction.overall_condition_notes),
        defects=extraction.defects,
    )
