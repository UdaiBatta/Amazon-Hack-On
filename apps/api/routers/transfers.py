"""Final transfer confirmation (mock ledger).

POST /transfers/{id}/confirm → buyer confirms received-as-described →
releases refund/payment and emits the journey-complete event.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from domain import events
from domain.events import bus
from domain.models import SessionState
from domain.store import store
from services.matching import haversine_km

# Ghosted "old world" route for the journey-comparison moneyshot.
OLD_WORLD = {"distance_km": 3500, "warehouses": 2, "days": 19}


router = APIRouter(prefix="/transfers", tags=["transfers"])


@router.post("/{transfer_id}/confirm")
async def confirm(transfer_id: str):
    transfer = store.get_transfer(transfer_id)
    if not transfer:
        raise HTTPException(404, "Transfer not found")
    session = store.get_session(transfer.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    transfer.status = "confirmed"
    session.state = SessionState.confirmed

    buyer = next((b for b in store.buyers if b.id == transfer.buyer_id), None)
    relay_km = (
        haversine_km(session.seller_lat, session.seller_lng, buyer.lat, buyer.lng)
        if buyer else 0.0
    )

    # Sustainability: ~0.6 kg CO2e per km of avoided long-haul (illustrative).
    km_avoided = OLD_WORLD["distance_km"] - relay_km
    co2_avoided = round(km_avoided * 0.0006, 2)

    bus.emit(
        transfer.session_id,
        events.TRANSFER_CONFIRMED,
        actor="buyer",
        detail={"relay_km": relay_km, "km_avoided": km_avoided},
    )
    return {
        "status": "confirmed",
        "refund_released": True,
        "payment_released": True,
        "mock": True,
        "journey": {
            "relay": {"distance_km": relay_km, "warehouses": 0, "days": 1,
                      "hops": 1},
            "old_world": OLD_WORLD,
            "km_avoided": round(km_avoided, 1),
            "co2e_avoided_kg": co2_avoided,
        },
    }
