"""Core domain models. Same shapes whether stored in DynamoDB or in-memory.

Data model (Section 11.3):
  Item · ReturnSession · Buyer · Transfer · events (append-only custody ledger)
"""
from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from ai.schemas import Defect


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def now_ms() -> int:
    return int(time.time() * 1000)


# --------------------------------------------------------------------------- #
# Grading / disposition enums
# --------------------------------------------------------------------------- #
class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Disposition(str, Enum):
    relay = "DIRECT_RELAY"
    liquidate = "LIQUIDATION"
    recycle = "RECYCLE"
    review = "MANUAL_REVIEW"


class SessionState(str, Enum):
    initiated = "initiated"
    scanning = "scanning"
    verifying = "verifying"
    grading = "grading"
    fraud_review = "fraud_review"
    disposition = "disposition"
    matched = "matched"
    in_transit = "in_transit"
    confirmed = "confirmed"


# --------------------------------------------------------------------------- #
# Fingerprint (the "birth certificate")
# --------------------------------------------------------------------------- #
class Fingerprint(BaseModel):
    embedding: list[float] = Field(default_factory=list)
    phash: str = ""
    serial: str = ""


class FingerprintMatch(BaseModel):
    embedding_sim: float = 0.0
    phash_dist: float = 0.0
    serial_match: bool = False
    composite: float = 0.0
    verdict: str = "pending"  # pass | extra_angle | fraud
    detected_serial: Optional[str] = None
    expected_serial: Optional[str] = None


# --------------------------------------------------------------------------- #
# Catalog
# --------------------------------------------------------------------------- #
class CaptureStep(BaseModel):
    key: str
    instruction: str
    required: bool = True


class Item(BaseModel):
    sku: str
    name: str
    serial: str
    base_price: float
    catalog_imgs: list[str] = Field(default_factory=list)
    capture_checklist: list[CaptureStep] = Field(default_factory=list)
    fingerprint: Fingerprint = Field(default_factory=Fingerprint)


# --------------------------------------------------------------------------- #
# Buyers / demand
# --------------------------------------------------------------------------- #
class WishlistEntry(BaseModel):
    sku: str
    max_price: float
    condition_min: Grade = Grade.C


class Buyer(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    wishlist: list[WishlistEntry] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Events — append-only custody ledger
# --------------------------------------------------------------------------- #
class Event(BaseModel):
    id: str = Field(default_factory=lambda: _id("evt"))
    session_id: str
    type: str
    actor: str
    ts: int = Field(default_factory=now_ms)
    geohash: Optional[str] = None
    detail: dict = Field(default_factory=dict)
    mock: bool = False


# --------------------------------------------------------------------------- #
# Return session — the aggregate root
# --------------------------------------------------------------------------- #
class CapturedFrame(BaseModel):
    step_key: str
    image_ref: str
    quality_score: float = 0.0
    ts: int = Field(default_factory=now_ms)


class GradeResult(BaseModel):
    grade: Grade
    score: float
    confidence: float
    rationale: str = ""
    defects: list[Defect] = Field(default_factory=list)
    # Coarse Rekognition DetectLabels that corroborate the AI defect map. Display /
    # audit only — never feeds the deterministic score (see services/grading.py).
    supporting_labels: list[dict] = Field(default_factory=list)


class PriceResult(BaseModel):
    resale_value: float
    instant_refund: float
    pct_of_new: float
    rationale: str = ""


class TrustScore(BaseModel):
    score: float
    fingerprint: FingerprintMatch
    behavioral_flags: list[str] = Field(default_factory=list)
    passed: bool = True


class DispositionResult(BaseModel):
    path: Disposition
    explanation: str = ""
    price: Optional[PriceResult] = None


class ReturnSession(BaseModel):
    id: str = Field(default_factory=lambda: _id("ses"))
    sku: str
    order_id: str
    state: SessionState = SessionState.initiated
    reason: str = ""
    seller_lat: float = 0.0
    seller_lng: float = 0.0
    frames: list[CapturedFrame] = Field(default_factory=list)
    scan_embedding: Optional[list[float]] = None  # real local embedding when photos flow
    extraction: Optional[dict] = None  # raw DefectExtraction
    fingerprint_match: Optional[FingerprintMatch] = None
    grade: Optional[GradeResult] = None
    price: Optional[PriceResult] = None
    trust: Optional[TrustScore] = None
    disposition: Optional[DispositionResult] = None
    certificate_id: Optional[str] = None
    created_at: int = Field(default_factory=now_ms)


class Transfer(BaseModel):
    id: str = Field(default_factory=lambda: _id("trf"))
    session_id: str
    buyer_id: str
    label_url: str
    tracking: str
    status: str = "reserved"  # reserved | picked_up | delivered | confirmed
    mock: bool = True
