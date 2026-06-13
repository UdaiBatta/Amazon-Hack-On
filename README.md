# RELAY AI — Returns That Never Return

> The trust and routing layer for reverse commerce. Doorstep AI inspection mints a
> trust certificate, catches swap-fraud live, and routes a returned item directly to a
> nearby buyer — so **the item never touches a warehouse.**

This is the 48-hour hackathon build. It is the *target architecture with the network
calls removed* — the FastAPI monolith has the same module boundaries as the
event-driven AWS system on the architecture slide.

## What's real vs mocked (the honesty rule)

| Capability | Status |
|---|---|
| Defect detection (Claude vision) | **REAL** |
| Fingerprint identity (embeddings + pHash + serial OCR) | **REAL** |
| Grading (deterministic rubric over AI-extracted defects) | **REAL** |
| Disposition routing (rules + AI explanation) | **REAL** |
| Buyer matching (haversine over seeded waitlist) | **REAL** logic, **SEEDED** data |
| Carrier booking | **MOCKED** (real interface, badged in ops dashboard) |
| Payments / refund ledger | **MOCKED** |
| Delivery-time fingerprint capture | **SEEDED** (captured by courier in production) |

The ops dashboard shows `MOCK` badges on every mocked service. When a judge asks
"what's live?", flip the dashboard.

## Philosophy: AI perceives, rules decide

Claude extracts structured defects; a deterministic rubric (in config, not in the
prompt) converts them to a grade. Grades are consistent and defensible.

## Repo structure

```
relay/
├── apps/
│   ├── api/    # FastAPI monolith (the brain)
│   └── web/    # React + Vite + Tailwind (consumer + buyer + ops)
└── packages/
    └── contracts/   # OpenAPI + event + JSON schemas (source of truth)
```

## Quickstart

```bash
# Backend
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd apps/web
npm install
npm run dev
```

The backend runs fully offline with seeded data and the fallback ladder. Set
`RELAY_AI_MODE=bedrock` (and AWS creds) or `RELAY_AI_MODE=anthropic` (and
`ANTHROPIC_API_KEY`) to enable live AI calls.
