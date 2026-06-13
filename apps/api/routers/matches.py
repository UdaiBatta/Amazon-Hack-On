"""Buyer matching + reservation (mock carrier inside).

GET  /matches/{session_id}   → ranked buyer candidates + demand pins (the map)
POST /matches/{session_id}/reserve → buyer reserves → books mock carrier shipment
"""
from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException

from domain import events
from domain.events import bus
from domain.models import SessionState
from domain.store import store
from services import matching as matching_svc
from services.carrier_mock import carrier

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/{session_id}")
async def get_matches(session_id: str):
    session = store.get_session(session_id)
    if not session or not session.grade or not session.price:
        raise HTTPException(400, "Session not graded yet")

    candidates = matching_svc.find_matches(
        sku=session.sku,
        grade=session.grade.grade,
        resale_price=session.price.resale_value,
        seller_lat=session.seller_lat,
        seller_lng=session.seller_lng,
    )
    if candidates:
        bus.emit(
            session_id,
            events.BUYER_MATCHED,
            actor="system",
            detail={"top_buyer": candidates[0]["buyer_name"],
                    "distance_km": candidates[0]["distance_km"]},
        )
    return {
        "seller": {"lat": session.seller_lat, "lng": session.seller_lng},
        "candidates": candidates,
        "demand_pins": matching_svc.demand_pins(session.sku),
        "price": session.price.model_dump(),
        "grade": session.grade.grade.value,
        "certificate_id": session.certificate_id,
    }


@router.post("/{session_id}/reserve")
async def reserve(session_id: str, buyer_id: str = Form(...)):
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    # Idempotent: if this session is already reserved (e.g. seller tab reserved,
    # then buyer tab reserves), return the existing booking instead of double-booking.
    existing = next(
        (t for t in store.transfers.values() if t.session_id == session_id), None
    )
    if existing:
        return {
            "transfer_id": existing.id,
            "tracking": existing.tracking,
            "label_url": existing.label_url,
            "status": existing.status,
            "pickup_window": "Tomorrow 10:00–12:00",
            "mock": True,
        }

    transfer = carrier.book(session_id, buyer_id)  # MOCK carrier (badged in ops)
    store.put_transfer(transfer)
    session.state = SessionState.in_transit
    bus.emit(
        session_id,
        events.SHIPMENT_BOOKED,
        actor="system",
        mock=True,
        detail={"transfer_id": transfer.id, "tracking": transfer.tracking,
                "buyer_id": buyer_id},
    )
    return {
        "transfer_id": transfer.id,
        "tracking": transfer.tracking,
        "label_url": transfer.label_url,
        "status": transfer.status,
        "pickup_window": "Tomorrow 10:00–12:00",
        "mock": True,
    }
