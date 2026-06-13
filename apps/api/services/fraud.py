"""Trust scoring (Section 4). Composite of fingerprint identity × serial × a few
behavioral flags. Below threshold → manual review with the full evidence bundle.

"AI flags, humans accuse." A fraud interrupt never auto-accuses; it routes to review.
"""
from __future__ import annotations

from config import settings
from domain.models import FingerprintMatch, TrustScore


def score(
    fp: FingerprintMatch,
    days_since_delivery: int = 18,
    return_count_30d: int = 1,
    reason_defect_consistent: bool = True,
) -> TrustScore:
    flags: list[str] = []

    # Behavioral signals (simplified, 3-4 features per the doc).
    if not fp.serial_match:
        flags.append(
            f"Serial mismatch: presented {fp.detected_serial} vs delivered {fp.expected_serial}"
        )
    if fp.composite < settings.fp_review_threshold:
        flags.append("Fingerprint identity below review threshold")
    if return_count_30d >= 4:
        flags.append("High return frequency (4+ in 30 days)")
    if days_since_delivery <= 1:
        flags.append("Return within 24h of delivery (wardrobing pattern)")
    if not reason_defect_consistent:
        flags.append("Stated reason inconsistent with detected defects")

    # Trust score is anchored on identity composite, penalised by flags.
    base = fp.composite
    penalty = 0.15 * len(flags)
    trust = max(0.0, round(base - penalty, 4))
    passed = trust >= settings.trust_threshold and fp.verdict != "fraud"

    return TrustScore(
        score=trust, fingerprint=fp, behavioral_flags=flags, passed=passed
    )
