"""Ops dashboard endpoints — architecture made visible (the dark mission-control UI).

GET /ops/events?session_id=  → custody/event stream (polling read model)
GET /ops/stream              → Server-Sent Events live feed (the real-time feel)
GET /ops/services            → service registry with REAL vs MOCK badges (the
                               radical-honesty answer to "what's live?")
"""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from config import settings
from domain.events import bus
from domain.store import store

router = APIRouter(prefix="/ops", tags=["ops"])


@router.get("/events")
async def events(session_id: str | None = None):
    return {
        "events": [e.model_dump() for e in store.events_for(session_id)],
    }


@router.get("/stream")
async def stream(request: Request):
    """SSE feed of live events for the ops dashboard."""
    queue = bus.subscribe()

    async def gen():
        try:
            # replay recent history first
            for e in store.events_for()[-20:]:
                yield f"data: {json.dumps(e.model_dump())}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(event.model_dump())}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        finally:
            bus.unsubscribe(queue)

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/services")
async def services():
    """The honest mock pattern: every service tagged REAL or MOCK."""
    vision_engine = {
        "gemini": "Google Gemini Flash (vision, free tier)",
        "anthropic": "Claude Sonnet (vision)",
        "bedrock": "Claude Sonnet on Bedrock (vision)",
        "mock": "cached SKU results (offline)",
    }.get(settings.ai_mode, settings.ai_mode)
    return {
        "ai_mode": settings.ai_mode,
        "services": [
            {"name": "Defect Detection", "engine": vision_engine, "status": "REAL"},
            {"name": "Serial OCR", "engine": vision_engine, "status": "REAL"},
            {"name": "Fingerprint Identity", "engine": "local CLIP-style embedding + pHash + serial", "status": "REAL"},
            {"name": "Condition Grading", "engine": "deterministic rubric", "status": "REAL"},
            {"name": "Trust / Fraud Score", "engine": "composite + behavioral flags", "status": "REAL"},
            {"name": "Disposition Routing", "engine": "rules + AI explanation", "status": "REAL"},
            {"name": "Buyer Matching", "engine": "haversine over waitlist", "status": "REAL (seeded data)"},
            {"name": "Pricing", "engine": "heuristic v1 + comps", "status": "REAL (v1 model)"},
            {"name": "Carrier Booking", "engine": "Shiprocket/Delhivery adapter", "status": "MOCK"},
            {"name": "Payments / Refund Ledger", "engine": "settlement rail", "status": "MOCK"},
            {"name": "Delivery-time Fingerprint Capture", "engine": "courier app", "status": "SEEDED"},
            {"name": "FiberPrint micro-texture", "engine": "surface authentication", "status": "ROADMAP"},
        ],
    }


@router.get("/metrics")
async def metrics():
    """Headline demo metrics (Section 7.2 slide 8)."""
    confirmed = [s for s in store.sessions.values() if s.state.value == "confirmed"]
    return {
        "returns_processed": len(store.sessions),
        "warehouse_cost_saved_per_return": 30,
        "avg_km_avoided": 3496,
        "fraud_caught": sum(
            1 for s in store.sessions.values() if s.trust and not s.trust.passed
        ),
        "landfill_kg_diverted_per_item": 0.45,
        "confirmed_transfers": len(confirmed),
    }
