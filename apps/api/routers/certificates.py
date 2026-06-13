"""The Trust Certificate — the product's icon. Public, QR-target.

GET /certificates/{certificate_id} → full certificate payload:
grade, defect map, identity confidence, fraud status, custody timeline.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from domain.store import store

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("/{certificate_id}")
async def get_certificate(certificate_id: str):
    session = next(
        (s for s in store.sessions.values() if s.certificate_id == certificate_id),
        None,
    )
    if not session or not session.grade:
        raise HTTPException(404, "Certificate not found")

    item = store.get_item(session.sku)
    custody = [
        {"type": e.type, "actor": e.actor, "ts": e.ts, "detail": e.detail}
        for e in store.events_for(session.id)
    ]
    return {
        "certificate_id": certificate_id,
        "product_name": item.name if item else session.sku,
        "sku": session.sku,
        "grade": session.grade.grade.value,
        "score": session.grade.score,
        "confidence": session.grade.confidence,
        "rationale": session.grade.rationale,
        "defects": [d.model_dump() for d in session.grade.defects],
        "identity_confidence": (
            session.fingerprint_match.composite if session.fingerprint_match else None
        ),
        "serial": session.fingerprint_match.detected_serial
        if session.fingerprint_match else None,
        "fraud_status": "passed" if (session.trust and session.trust.passed) else "flagged",
        "price": session.price.model_dump() if session.price else None,
        "custody_timeline": custody,
        "issued_at": session.created_at,
    }
