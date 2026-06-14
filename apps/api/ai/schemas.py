"""Pydantic mirrors of the JSON contracts the AI layer must honour.

Build this first — everything downstream (grading, fraud, pricing, certificate)
reads these shapes. The defect-extraction schema is forced on Claude via
tool-use / JSON mode, with retry-with-repair on parse failure (see ai/bedrock.py).
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    cosmetic = "cosmetic"
    minor = "minor"
    moderate = "moderate"
    major = "major"


class Defect(BaseModel):
    type: str = Field(..., description="e.g. scratch, scuff, dent, crack, stain")
    location: str = Field(..., description="human-readable location on the item")
    size_cm: Optional[float] = Field(None, description="approx longest dimension in cm")
    severity: Severity
    affects_function: bool = False
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class ProductMatch(BaseModel):
    matches_catalog: bool = True
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class SerialDetection(BaseModel):
    detected: Optional[str] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class DefectExtraction(BaseModel):
    """The single structured-output contract. Claude must return exactly this."""

    is_requested_view: bool = True
    product_match: ProductMatch = Field(default_factory=ProductMatch)
    serial_number: SerialDetection = Field(default_factory=SerialDetection)
    defects: list[Defect] = Field(default_factory=list)
    overall_condition_notes: str = ""


class FrameValidation(BaseModel):
    """Per-frame check: is this actually the requested view?"""

    is_requested_view: bool
    detected_view: str = ""
    redirect_message: Optional[str] = Field(
        None, description="natural-language redirect if the view is wrong"
    )
    confidence: float = Field(0.0, ge=0.0, le=1.0)
