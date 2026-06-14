"""Amazon Rekognition adapter — real AWS perception signals (Section: AI layer).

Two read-only calls, both behind graceful fallbacks so the 4-rung ladder
(live → cached → stub → review) still holds if AWS is slow/unavailable:

  extract_serial(image_bytes)        DetectText  → serial OCR (replaces seeded serial)
  detect_defect_labels(image_bytes)  DetectLabels → coarse defect-relevant labels,
                                     a *supporting* signal into the deterministic
                                     grading rubric (NOT the primary defect source —
                                     that stays Gemini/cached per design).

Both return safe defaults (None / []) on any failure so the caller can fall back
to the cached/seeded value. Rules still decide; this only adds perception signal.

Cost (us-east-1, Group-1 APIs, as of 2025):
  DetectText   ≈ $0.001 / image  ($1.00 per 1,000 images)
  DetectLabels ≈ $0.001 / image  ($1.00 per 1,000 images)
  Free tier:   5,000 images/month free for the first 12 months → dev/testing ≈ $0.
A full scan (one serial frame + one defect frame) is ≈ $0.002 once past free tier.
"""
from __future__ import annotations

import re

from config import settings

# Serial heuristics. Demo units use SN-#####; we accept that plus a generic
# "looks like a serial" fallback (>=1 letter and >=3 digits in one token).
# Strong: an "S/N", "SN", or "SERIAL[ NO]" prefix followed by the actual token.
_SN_STRONG = re.compile(
    r"(?:S\s*[/\\]?\s*N|SERIAL(?:\s*(?:NO|NUMBER))?)\s*[:#-]?\s*([A-Z0-9][A-Z0-9-]{2,})",
    re.IGNORECASE,
)
_SERIALish = re.compile(r"^(?=.*[A-Z])(?=(?:.*\d){3,})[A-Z0-9-]{5,}$", re.IGNORECASE)

# DetectLabels returns coarse object/scene labels; these are the ones we treat as
# (weak) condition signals. The real defect map comes from the vision model.
_DEFECT_LABEL_KEYWORDS = {
    "scratch", "scratches", "dent", "dented", "damage", "damaged", "wear",
    "worn", "tear", "torn", "crack", "cracked", "scuff", "scuffed", "stain",
    "stained", "rust", "corrosion", "chip", "chipped", "abrasion", "scrape",
}

_client = None


def _rekognition():
    """Lazy boto3 client — uses the default credential chain + configured region."""
    global _client
    if _client is None:
        import boto3

        _client = boto3.client("rekognition", region_name=settings.aws_region)
    return _client


def extract_serial(image_bytes: bytes | None) -> str | None:
    """OCR the serial sticker via Rekognition DetectText.

    Returns the best serial-looking string (uppercased), or None if nothing
    convincing is found / the call fails — letting the caller keep the seeded
    serial so the demo's fraud invariant (SN-88412 vs SN-77109) is never broken.
    """
    if not image_bytes:
        return None
    try:
        resp = _rekognition().detect_text(Image={"Bytes": image_bytes})
    except Exception:
        return None

    detections = resp.get("TextDetections", [])
    # Prefer whole LINEs (serials are usually one token/line), then WORDs.
    candidates: list[tuple[float, str]] = []
    for d in detections:
        text = (d.get("DetectedText") or "").strip()
        conf = float(d.get("Confidence", 0.0))
        if not text:
            continue
        candidates.append((conf, text))

    # Pass 1: explicit "S/N ..." prefix anywhere in the detected text.
    for _, text in sorted(candidates, key=lambda c: -c[0]):
        m = _SN_STRONG.search(text)
        if m:
            token = m.group(1).upper().strip("-")
            # If OCR already captured the "SN-" prefix in the token, don't double it.
            return token if token.startswith("SN-") else f"SN-{token}"

    # Pass 2: any single token that looks like a serial (letters + >=3 digits).
    for _, text in sorted(candidates, key=lambda c: -c[0]):
        token = text.replace(" ", "")
        if _SERIALish.match(token):
            return token.upper()

    return None


def detect_defect_labels(image_bytes: bytes | None) -> list[dict]:
    """DetectLabels → coarse defect-relevant labels as a supporting grading signal.

    Returns a list of {"label": str, "confidence": float} for labels that match
    our condition-keyword set, or [] on no match / failure. This NEVER decides a
    grade on its own — the rubric stays deterministic; this only nudges/corroborates.
    """
    if not image_bytes:
        return []
    try:
        resp = _rekognition().detect_labels(
            Image={"Bytes": image_bytes}, MaxLabels=25, MinConfidence=55.0
        )
    except Exception:
        return []

    out: list[dict] = []
    for label in resp.get("Labels", []):
        name = (label.get("Name") or "").strip()
        if name.lower() in _DEFECT_LABEL_KEYWORDS:
            out.append({"label": name, "confidence": round(float(label.get("Confidence", 0.0)), 2)})
    return out
