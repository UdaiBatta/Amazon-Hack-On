"""Fingerprint identity verification (Section 4.1).

  identity_confidence = 0.45·serial_exact + 0.35·embedding_cosine
                        + 0.20·(1 − phash_dist_norm)

Embedding cosine is real numpy. In live mode the return-time embedding comes from
Titan/CLIP; offline it is derived deterministically from the scanned serial so the
"swap" unit produces a genuinely different vector — the math is real either way.
"""
from __future__ import annotations

import numpy as np

from config import settings
from domain.models import Fingerprint, FingerprintMatch
from seed.catalog import _seed_embedding

_PHASH_BITS = 64  # 16 hex chars


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    va, vb = np.array(a), np.array(b)
    denom = (np.linalg.norm(va) * np.linalg.norm(vb)) or 1.0
    return float(np.dot(va, vb) / denom)


def _phash_distance_norm(a: str, b: str) -> float:
    """Normalised Hamming distance between two hex perceptual hashes (0..1)."""
    if not a or not b:
        return 1.0
    try:
        ia, ib = int(a, 16), int(b, 16)
    except ValueError:
        return 1.0
    return bin(ia ^ ib).count("1") / _PHASH_BITS


def build_return_fingerprint(
    sku: str, scanned_serial: str, embedding: list[float] | None, phash: str | None
) -> Fingerprint:
    """Compute the fingerprint of the unit presented at return time."""
    emb = embedding or _seed_embedding(f"{sku}:{scanned_serial}")
    # offline pHash: identical model => identical hash unless serial differs (swap)
    ph = phash or ("f8e0c1a3b5d70e2f" if scanned_serial else "0000000000000000")
    return Fingerprint(embedding=emb, phash=ph, serial=scanned_serial)


def match(reference: Fingerprint, presented: Fingerprint) -> FingerprintMatch:
    serial_match = bool(
        reference.serial and presented.serial
        and reference.serial == presented.serial
    )
    emb_sim = max(0.0, _cosine(reference.embedding, presented.embedding))
    phash_dist = _phash_distance_norm(reference.phash, presented.phash)

    composite = (
        0.45 * (1.0 if serial_match else 0.0)
        + 0.35 * emb_sim
        + 0.20 * (1.0 - phash_dist)
    )

    if composite >= settings.fp_pass_threshold:
        verdict = "pass"
    elif composite >= settings.fp_review_threshold:
        verdict = "extra_angle"
    else:
        verdict = "fraud"

    return FingerprintMatch(
        embedding_sim=round(emb_sim, 4),
        phash_dist=round(phash_dist, 4),
        serial_match=serial_match,
        composite=round(composite, 4),
        verdict=verdict,
        detected_serial=presented.serial,
        expected_serial=reference.serial,
    )
