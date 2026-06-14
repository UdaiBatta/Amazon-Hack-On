"""RELAY AI — FastAPI monolith entrypoint (routers only).

This is the target architecture with the network calls removed: the in-process
service modules have the same boundaries as the Step Functions / Lambda services
on the architecture slide.
"""
from __future__ import annotations

import asyncio
import contextlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai.bedrock import ai
from config import settings
from routers import (
    buyer,
    catalog,
    certificates,
    matches,
    ops,
    sessions,
    transfers,
)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm the model so the first demo inference isn't a cold-start death.
    await ai.prewarm()
    stop = asyncio.Event()

    async def keepwarm():
        while not stop.is_set():
            await ai.prewarm()
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(stop.wait(), timeout=60)

    task = asyncio.create_task(keepwarm())
    yield
    stop.set()
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="RELAY AI", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo-wide; tighten per-origin for production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog.router)
app.include_router(sessions.router)
app.include_router(matches.router)
app.include_router(buyer.router)
app.include_router(transfers.router)
app.include_router(certificates.router)
app.include_router(ops.router)


@app.get("/health")
async def health():
    return {"status": "ok", "ai_mode": settings.ai_mode}
