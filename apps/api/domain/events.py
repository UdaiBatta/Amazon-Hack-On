"""Event emitter — the EventBridge analogue. Every state transition appends to the
custody ledger (one write path, two read models: app reads state, ops/certificate
read the event log — "CQRS-lite").

Live subscribers (the ops dashboard) receive events over a broadcast queue.
"""
from __future__ import annotations

import asyncio
from typing import Optional

from domain.models import Event
from domain.store import store

# Canonical event types (first-class, like EventBridge):
RETURN_INITIATED = "return.initiated"
FRAME_ACCEPTED = "frame.accepted"
FRAME_REJECTED = "frame.rejected"
SCAN_COMPLETED = "scan.completed"
IDENTITY_VERIFIED = "identity.verified"
GRADED = "grade.completed"
FRAUD_FLAGGED = "fraud.flagged"
DISPOSITION_DECIDED = "disposition.decided"
BUYER_MATCHED = "buyer.matched"
SHIPMENT_BOOKED = "shipment.booked"
TRANSFER_CONFIRMED = "transfer.confirmed"


class EventBus:
    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self._subscribers:
            self._subscribers.remove(q)

    def emit(
        self,
        session_id: str,
        type: str,
        actor: str = "system",
        detail: Optional[dict] = None,
        mock: bool = False,
        geohash: Optional[str] = None,
    ) -> Event:
        event = Event(
            session_id=session_id,
            type=type,
            actor=actor,
            detail=detail or {},
            mock=mock,
            geohash=geohash,
        )
        store.append_event(event)
        for q in list(self._subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass
        return event


bus = EventBus()
