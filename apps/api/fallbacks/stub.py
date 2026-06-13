"""Rung 3 of the fallback ladder: a local rule-based stub. Never an error screen.

Produces a schema-valid DefectExtraction from the known catalog serial + a single
canned cosmetic defect, so the pipeline always completes.
"""
from __future__ import annotations

from domain.models import Item


def stub_extraction(item: Item) -> dict:
    return {
        "is_requested_view": True,
        "product_match": {"matches_catalog": True, "confidence": 0.7},
        "serial_number": {"detected": item.serial, "confidence": 0.7},
        "defects": [
            {
                "type": "scuff",
                "location": "surface",
                "size_cm": 1.5,
                "severity": "minor",
                "affects_function": False,
                "confidence": 0.6,
            }
        ],
        "overall_condition_notes": "Offline rule-based assessment; queued for inspector confirmation.",
    }
