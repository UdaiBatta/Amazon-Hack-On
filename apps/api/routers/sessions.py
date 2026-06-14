"""Session lifecycle: the return brain's state machine, exposed as endpoints.

POST /sessions                  → create ReturnSession + capture checklist
POST /sessions/{id}/frames      → submit a captured frame (guided scan)
POST /sessions/{id}/verify      → fingerprint identity + trust/fraud screen
POST /sessions/{id}/grade       → defect extraction + grade + price + certificate
POST /sessions/{id}/disposition → routing decision
"""
from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from config import settings
from domain import events
from domain.events import bus
from domain.models import (
    CapturedFrame,
    GradeResult,
    ReturnSession,
    SessionState,
)
from domain.store import store
from fallbacks.cached import CACHED_SERIAL
from seed.catalog import DEMO_ORDER
from services import defects as defects_svc
from services import disposition as disposition_svc
from services import fingerprint as fp_svc
from services import fraud as fraud_svc
from services import grading as grading_svc
from services import matching as matching_svc
from services import pricing as pricing_svc
from services import rekognition as rekognition_svc

router = APIRouter(prefix="/sessions", tags=["sessions"])


# --------------------------------------------------------------------------- #
# Create
# --------------------------------------------------------------------------- #
@router.post("")
async def create_session(
    sku: str = Form(...),
    order_id: str = Form(DEMO_ORDER["order_id"]),
    reason: str = Form("Changed my mind"),
):
    item = store.get_item(sku)
    if not item:
        raise HTTPException(404, f"Unknown SKU {sku}")

    session = ReturnSession(
        sku=sku,
        order_id=order_id,
        reason=reason,
        state=SessionState.scanning,
        seller_lat=DEMO_ORDER["seller_lat"],
        seller_lng=DEMO_ORDER["seller_lng"],
    )
    store.put_session(session)
    bus.emit(
        session.id,
        events.RETURN_INITIATED,
        actor="seller",
        detail={"sku": sku, "order_id": order_id, "reason": reason},
    )
    return {
        "session_id": session.id,
        "checklist": [step.model_dump() for step in item.capture_checklist],
        "product_name": item.name,
    }


# --------------------------------------------------------------------------- #
# Frames (guided scan)
# --------------------------------------------------------------------------- #
@router.post("/{session_id}/frames")
async def submit_frame(
    session_id: str,
    step_key: str = Form(...),
    quality_score: float = Form(0.9),
    image: UploadFile | None = File(None),
):
    session = _get(session_id)
    item = store.get_item(session.sku)

    img_bytes = await image.read() if image else None
    # Keep the scan snappy: per-frame view validation uses the fast on-device path
    # (client quality gate + scripted redirect handle UX). The live vision model is
    # reserved for grade-time defect extraction, the high-value call. To enable real
    # per-frame Gemini validation later, pass img_bytes here instead of None.
    validation, _ = await defects_svc.ai.validate_frame(
        product_name=item.name,
        requested_view=step_key,
        image=None,
    )

    # Compute a real local embedding from the front view (zero-cost, on-device).
    if img_bytes:
        store.frame_bytes.setdefault(session_id, []).append(img_bytes)
        store.frames_by_step.setdefault(session_id, {})[step_key] = img_bytes
        if step_key in ("front", "side"):
            try:
                from services import embeddings as emb_svc

                session.scan_embedding = emb_svc.embed(img_bytes)
            except Exception:
                pass

    if not validation.get("is_requested_view", True):
        bus.emit(
            session_id,
            events.FRAME_REJECTED,
            actor="ai",
            detail={"step": step_key, "redirect": validation.get("redirect_message")},
        )
        return {
            "accepted": False,
            "reason": validation.get("redirect_message"),
            "next_step": step_key,
        }

    frame = CapturedFrame(
        step_key=step_key,
        image_ref=f"raw/{session_id}/{step_key}.jpg",
        quality_score=quality_score,
    )
    session.frames.append(frame)
    bus.emit(
        session_id,
        events.FRAME_ACCEPTED,
        actor="ai",
        detail={"step": step_key, "quality": quality_score},
    )

    captured = {f.step_key for f in session.frames}
    required = {s.key for s in item.capture_checklist if s.required}
    remaining = [s.key for s in item.capture_checklist if s.key not in captured]
    complete = required.issubset(captured)
    if complete:
        bus.emit(session_id, events.SCAN_COMPLETED, actor="ai",
                 detail={"frames": len(session.frames)})

    return {
        "accepted": True,
        "captured": sorted(captured),
        "next_step": remaining[0] if remaining else None,
        "scan_complete": complete,
    }


# --------------------------------------------------------------------------- #
# Verify (fingerprint + trust)
# --------------------------------------------------------------------------- #
@router.post("/{session_id}/verify")
async def verify(session_id: str, fraud_mode: bool = Form(False)):
    session = _get(session_id)
    item = store.get_item(session.sku)
    session.state = SessionState.verifying

    # The serial presented at return time. Seeded value is the demo-safe default
    # (fraud demo presents the swap unit's serial). When AWS mode is active, real
    # Rekognition OCR of the serial frame overrides the seed if it reads convincingly;
    # otherwise we keep the seed so the fraud invariant (SN-88412 vs SN-77109) holds.
    presented_serial = "SN-88412" if fraud_mode else item.serial
    serial_source = "seed"
    # Fraud demo is scripted to present the swap unit's serial — never OCR-override it.
    if settings.ai_mode == "aws" and not fraud_mode:
        serial_frame = store.frames_by_step.get(session_id, {}).get("serial")
        ocr_serial = rekognition_svc.extract_serial(serial_frame)
        if ocr_serial:  # rung 1: live Rekognition OCR
            presented_serial = ocr_serial
            serial_source = "rekognition"
        elif item.sku in CACHED_SERIAL:  # rung 2: cached real OCR
            presented_serial = CACHED_SERIAL[item.sku]
            serial_source = "cache"
        # rung 3: seeded catalog serial (already assigned above)

    # Use real local embeddings when both a scanned image and a catalog reference
    # image exist; otherwise fall back to seeded vectors (offline demo-safe).
    from services import embeddings as emb_svc

    ref_emb = emb_svc.reference_embedding(item.sku)
    use_real = (
        not fraud_mode
        and session.scan_embedding is not None
        and ref_emb is not None
    )
    reference_fp = item.fingerprint
    presented_embedding = None
    if use_real:
        reference_fp = item.fingerprint.model_copy(update={"embedding": list(ref_emb)})
        presented_embedding = session.scan_embedding

    presented = fp_svc.build_return_fingerprint(
        sku=item.sku,
        scanned_serial=presented_serial,
        embedding=presented_embedding,
        phash=None,
    )
    fp_match = fp_svc.match(reference_fp, presented)
    session.fingerprint_match = fp_match

    trust = fraud_svc.score(fp_match)
    session.trust = trust

    bus.emit(
        session_id,
        events.IDENTITY_VERIFIED,
        actor="ai",
        detail={
            "composite": fp_match.composite,
            "serial_match": fp_match.serial_match,
            "verdict": fp_match.verdict,
            "serial_source": serial_source,
        },
    )
    if not trust.passed:
        session.state = SessionState.fraud_review
        bus.emit(
            session_id,
            events.FRAUD_FLAGGED,
            actor="ai",
            detail={"flags": trust.behavioral_flags, "trust": trust.score},
        )

    return {
        "identity_confidence": fp_match.composite,
        "embedding_sim": fp_match.embedding_sim,
        "phash_dist": fp_match.phash_dist,
        "serial_match": fp_match.serial_match,
        "detected_serial": fp_match.detected_serial,
        "expected_serial": fp_match.expected_serial,
        "verdict": fp_match.verdict,
        "trust_score": trust.score,
        "trust_passed": trust.passed,
        "behavioral_flags": trust.behavioral_flags,
    }


# --------------------------------------------------------------------------- #
# Grade (defects + rubric + price + certificate)
# --------------------------------------------------------------------------- #
@router.post("/{session_id}/grade")
async def grade_session(session_id: str, fraud_mode: bool = Form(False)):
    session = _get(session_id)
    item = store.get_item(session.sku)

    # Idempotent: if this session was already graded, return the SAME result so the
    # certificate screen and the disposition screen can never disagree (and we don't
    # re-call the vision model, which in live mode could return a different grade).
    if session.grade and session.price and session.certificate_id:
        return {
            "grade": session.grade.grade.value,
            "score": session.grade.score,
            "confidence": session.grade.confidence,
            "rationale": session.grade.rationale,
            "defects": [d.model_dump() for d in session.grade.defects],
            "price": session.price.model_dump(),
            "certificate_id": session.certificate_id,
            "ai_source": "cache",
        }

    session.state = SessionState.grading

    # Feed real captured frames to the live vision model when present; the cached
    # SKU result stands behind it as the fallback (offline demo-safe).
    images = store.frame_bytes.get(session_id, [])
    extraction, source = await defects_svc.extract(item, images=images, fraud_mode=fraud_mode)
    session.extraction = extraction.model_dump()

    # AWS mode: Rekognition DetectLabels on the front frame as a *supporting* signal.
    # Corroboration/annotation only — the rubric in grading_svc stays deterministic.
    support_labels: list[dict] = []
    if settings.ai_mode == "aws":
        front_frame = store.frames_by_step.get(session_id, {}).get("front")
        support_labels = rekognition_svc.detect_defect_labels(front_frame)

    grade_result: GradeResult = grading_svc.grade(extraction, support_labels=support_labels)
    session.grade = grade_result

    price_result = pricing_svc.price(item, grade_result.grade)
    session.price = price_result

    session.certificate_id = f"RLY-{session.id[-6:].upper()}"
    bus.emit(
        session_id,
        events.GRADED,
        actor="ai",
        detail={
            "grade": grade_result.grade.value,
            "score": grade_result.score,
            "source": source,
            "certificate_id": session.certificate_id,
        },
    )
    return {
        "grade": grade_result.grade.value,
        "score": grade_result.score,
        "confidence": grade_result.confidence,
        "rationale": grade_result.rationale,
        "defects": [d.model_dump() for d in grade_result.defects],
        "price": price_result.model_dump(),
        "certificate_id": session.certificate_id,
        "ai_source": source,
    }


# --------------------------------------------------------------------------- #
# Disposition (routing)
# --------------------------------------------------------------------------- #
@router.post("/{session_id}/disposition")
async def disposition(session_id: str):
    session = _get(session_id)
    if not (session.grade and session.price and session.trust):
        raise HTTPException(400, "Session not graded yet")
    session.state = SessionState.disposition

    matches = matching_svc.find_matches(
        sku=session.sku,
        grade=session.grade.grade,
        resale_price=session.price.resale_value,
        seller_lat=session.seller_lat,
        seller_lng=session.seller_lng,
    )
    nearest_km = matches[0]["distance_km"] if matches else None

    result = disposition_svc.decide(
        grade=session.grade,
        price=session.price,
        trust=session.trust,
        nearby_demand=len(matches),
        nearest_km=nearest_km,
    )
    # AI explains; the rule above already decided the path. AWS mode rephrases the
    # explanation via Bedrock Haiku, else keeps the deterministic text (fallback ladder).
    result, explanation_source = await disposition_svc.explain(
        result,
        facts={
            "grade": session.grade.grade.value,
            "resale_value": session.price.resale_value,
            "nearby_demand": len(matches),
            "nearest_km": nearest_km,
        },
        sku=session.sku,
    )
    session.disposition = result
    bus.emit(
        session_id,
        events.DISPOSITION_DECIDED,
        actor="system",
        detail={
            "path": result.path.value,
            "explanation": result.explanation,
            "explanation_source": explanation_source,
        },
    )
    return {
        "path": result.path.value,
        "explanation": result.explanation,
        "price": result.price.model_dump() if result.price else None,
        "match_count": len(matches),
    }


@router.get("/{session_id}")
async def get_session(session_id: str):
    return _get(session_id).model_dump()


def _get(session_id: str) -> ReturnSession:
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session
