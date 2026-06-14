"""Seeded catalog: 3 photogenic, defect-visible SKUs (Section 3.4 "constrain the
universe"). Fingerprints here represent the delivery-time "birth certificate" the
courier captures in production — seeded honestly for the demo.

Embeddings are short deterministic vectors so fingerprint math is real and stable
offline. In live mode they are replaced by Titan/CLIP embeddings.
"""
from __future__ import annotations

import hashlib

from domain.models import CaptureStep, Fingerprint, Item


def _seed_embedding(seed: str, dim: int = 32) -> list[float]:
    """Deterministic pseudo-embedding from a seed string (stable across runs)."""
    out: list[float] = []
    counter = 0
    while len(out) < dim:
        h = hashlib.sha256(f"{seed}:{counter}".encode()).digest()
        for b in h:
            out.append((b / 255.0) * 2 - 1)
            if len(out) >= dim:
                break
        counter += 1
    # normalise
    norm = sum(x * x for x in out) ** 0.5 or 1.0
    return [x / norm for x in out]


HEADPHONE_CHECKLIST = [
    CaptureStep(key="front", instruction="Show the front of the headphones"),
    CaptureStep(key="serial", instruction="Show the serial sticker under the left earcup"),
    CaptureStep(key="left_hinge", instruction="Tilt to catch the left hinge under light"),
    CaptureStep(key="earcups", instruction="Closer on both earcups"),
]

SHOE_CHECKLIST = [
    CaptureStep(key="side", instruction="Show the outer side of the shoe"),
    CaptureStep(key="sole", instruction="Flip to show the sole"),
    CaptureStep(key="serial", instruction="Show the size/serial tag inside the tongue"),
    CaptureStep(key="toe", instruction="Closer on the toe box"),
]

APPLIANCE_CHECKLIST = [
    CaptureStep(key="front", instruction="Show the front panel"),
    CaptureStep(key="serial", instruction="Show the rating/serial label on the base"),
    CaptureStep(key="cord", instruction="Show the power cord and plug"),
    CaptureStep(key="top", instruction="Closer on the top surface"),
]


CATALOG: dict[str, Item] = {
    "SKU-HP-01": Item(
        sku="SKU-HP-01",
        name="JBL Tune 770NC Wireless Headphones (Black)",
        serial="SN-77109",
        base_price=5599.0,
        catalog_imgs=["catalog/hp01_front.jpg", "catalog/hp01_side.jpg"],
        capture_checklist=HEADPHONE_CHECKLIST,
        fingerprint=Fingerprint(
            embedding=_seed_embedding("SKU-HP-01:SN-77109"),
            phash="f8e0c1a3b5d70e2f",
            serial="SN-77109",
        ),
    ),
    "SKU-SH-01": Item(
        sku="SKU-SH-01",
        name="Nike Pegasus 41 Running Shoe",
        serial="NK-40219",
        base_price=11995.0,
        catalog_imgs=["catalog/sh01_side.jpg"],
        capture_checklist=SHOE_CHECKLIST,
        fingerprint=Fingerprint(
            embedding=_seed_embedding("SKU-SH-01:NK-40219"),
            phash="a1b2c3d4e5f60718",
            serial="NK-40219",
        ),
    ),
    "SKU-AP-01": Item(
        sku="SKU-AP-01",
        name="Nespresso Vertuo Pop Coffee Machine",
        serial="NP-55831",
        base_price=8999.0,
        catalog_imgs=["catalog/ap01_front.jpg"],
        capture_checklist=APPLIANCE_CHECKLIST,
        fingerprint=Fingerprint(
            embedding=_seed_embedding("SKU-AP-01:NP-55831"),
            phash="0f1e2d3c4b5a6978",
            serial="NP-55831",
        ),
    ),
}

# Pre-seeded order the demo seller is returning.
DEMO_ORDER = {
    "order_id": "ORD-402-7781993",
    "sku": "SKU-HP-01",
    "seller_lat": 30.3398,   # Patiala — matches the Section 1.7 story
    "seller_lng": 76.3869,
}
