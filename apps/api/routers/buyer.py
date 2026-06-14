"""Buyer-side surface (Section 2, Steps 9 & 11).

The buyer (Rohan) sees a push card for any verified item where they are the top
match, can reserve it, and later confirms receipt. Single shared store means the
buyer's phone and the seller's phone read the same live session.

GET /buyer/{buyer_id}/feed → reservable + in-transit matches for this buyer
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from domain.models import SessionState
from domain.store import store
from services import matching as matching_svc

router = APIRouter(prefix="/buyer", tags=["buyer"])

# states where an item is relevant to the buyer's feed
_FEED_STATES = {
    SessionState.disposition,
    SessionState.matched,
    SessionState.in_transit,
    SessionState.confirmed,
}


@router.get("/{buyer_id}/feed")
async def feed(buyer_id: str):
    buyer = next((b for b in store.buyers if b.id == buyer_id), None)
    if not buyer:
        raise HTTPException(404, "Unknown buyer")

    cards: list[dict] = []
    # newest first
    for session in sorted(
        store.sessions.values(), key=lambda s: s.created_at, reverse=True
    ):
        if session.state not in _FEED_STATES:
            continue
        if not (session.grade and session.price):
            continue

        candidates = matching_svc.find_matches(
            sku=session.sku,
            grade=session.grade.grade,
            resale_price=session.price.resale_value,
            seller_lat=session.seller_lat,
            seller_lng=session.seller_lng,
        )
        top = candidates[0] if candidates else None
        if not top or top["buyer_id"] != buyer_id:
            continue

        item = store.get_item(session.sku)
        transfer = next(
            (t for t in store.transfers.values() if t.session_id == session.id), None
        )
        cards.append(
            {
                "session_id": session.id,
                "product_name": item.name if item else session.sku,
                "grade": session.grade.grade.value,
                "price": session.price.resale_value,
                "distance_km": top["distance_km"],
                "certificate_id": session.certificate_id,
                "state": session.state.value,
                "reserved": transfer is not None,
                "transfer_id": transfer.id if transfer else None,
                "tracking": transfer.tracking if transfer else None,
                "transfer_status": transfer.status if transfer else None,
                "defect_count": len(session.grade.defects),
                "identity_confidence": (
                    session.fingerprint_match.composite
                    if session.fingerprint_match
                    else None
                ),
            }
        )

    return {"buyer_id": buyer_id, "buyer_name": buyer.name, "cards": cards}
