"""Cached happy-path AI responses per demo SKU (rung 2 of the fallback ladder).

Identical schema to a live Claude response. If the live call is slow or offline,
the UI shows these at the 4-second mark ("optimistic resolve"). Honest: these are
pre-run results for the demo SKUs, not fabricated live calls.
"""
from __future__ import annotations

# Keyed by SKU. Each is a valid DefectExtraction dict.
CACHED_DEFECTS: dict[str, dict] = {
    "SKU-HP-01": {
        "is_requested_view": True,
        "product_match": {"matches_catalog": True, "confidence": 0.96},
        "serial_number": {"detected": "SN-77109", "confidence": 0.98},
        # Real Gemini (gemini-2.5-flash-lite) output on the actual JBL Tune 770NC
        # front photo, captured Session 3 and cached for demo reliability (free
        # tier is ~20 calls/day). Serial is from the serial-sticker capture step.
        "defects": [
            {
                "type": "wear",
                "location": "left earcup exterior edge",
                "size_cm": 1.5,
                "severity": "minor",
                "affects_function": False,
                "confidence": 0.85,
            },
            {
                "type": "wear",
                "location": "right earcup exterior edge",
                "size_cm": 1.2,
                "severity": "minor",
                "affects_function": False,
                "confidence": 0.85,
            },
            {
                "type": "wear",
                "location": "headband padding, center",
                "size_cm": 2.0,
                "severity": "minor",
                "affects_function": False,
                "confidence": 0.80,
            },
            {
                "type": "scuff",
                "location": "left earcup surface",
                "size_cm": 0.8,
                "severity": "cosmetic",
                "affects_function": False,
                "confidence": 0.75,
            },
        ],
        "overall_condition_notes": "Minor signs of wear on the earcup edges and headband padding, consistent with regular use; otherwise good cosmetic condition.",
    },
    "SKU-SH-01": {
        "is_requested_view": True,
        "product_match": {"matches_catalog": True, "confidence": 0.94},
        "serial_number": {"detected": "NK-40219", "confidence": 0.91},
        "defects": [
            {
                "type": "wear",
                "location": "outsole heel",
                "size_cm": 3.5,
                "severity": "moderate",
                "affects_function": False,
                "confidence": 0.83,
            }
        ],
        "overall_condition_notes": "Tried-on with light outsole wear; upper clean, no creasing.",
    },
    "SKU-AP-01": {
        "is_requested_view": True,
        "product_match": {"matches_catalog": True, "confidence": 0.95},
        "serial_number": {"detected": "NP-55831", "confidence": 0.96},
        "defects": [],
        "overall_condition_notes": "Appears unused; no scratches or water marks on the housing.",
    },
}

# The planted fraud unit: a different physical headphone unit (Section 7).
CACHED_FRAUD_UNIT: dict = {
    "is_requested_view": True,
    "product_match": {"matches_catalog": True, "confidence": 0.93},
    "serial_number": {"detected": "SN-88412", "confidence": 0.97},
    "defects": [
        {
            "type": "scratch",
            "location": "right earcup, multiple",
            "size_cm": 4.0,
            "severity": "moderate",
            "affects_function": False,
            "confidence": 0.9,
        }
    ],
    "overall_condition_notes": "Heavier wear than expected; serial does not match the delivered unit.",
}
