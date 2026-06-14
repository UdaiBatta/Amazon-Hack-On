# RELAY AI — Returns That Never Return

**The trust and routing layer for reverse commerce.** A doorstep AI inspection mints
a trust certificate, catches swap fraud live, and routes a returned item straight to a
nearby buyer, so **the item never touches a warehouse.**

> The warehouse exists in the returns loop for one reason: it is the only place anyone
> trusts to verify an item's condition. RELAY moves that trust to the doorstep, so the
> return never has to travel back. Returns become transfers.

Built for HackOn with Amazon, Season 6.0. Theme: Second Life Commerce, AI-Powered
Returns and Sustainable Resale.

---

## The three surfaces

| Route | Who | What |
|---|---|---|
| `/` | Seller (Asha) | Amazon-style order list, guided AI scan, fingerprint check, grade certificate, fraud screen, buyer match map, journey reveal |
| `/buyer` | Buyer (Rohan) | Live demand feed, reserve a verified item, confirm on delivery |
| `/ops` | Operations | Dark mission-control: live event stream, REAL vs MOCK service registry, impact metrics |

## Philosophy: AI perceives, rules decide

The vision model extracts structured defects and reads the serial. A deterministic
rubric (in config, not in the prompt) turns that into a grade, a price, and a routing
decision. Outcomes stay consistent, auditable, and defensible. Fraud interrupts route
to human review with the full evidence bundle. AI flags, humans accuse.

## AI modes (one switch, four providers)

Set `RELAY_AI_MODE` in `apps/api/.env`:

| Mode | Perception | Cost |
|---|---|---|
| `mock` | cached / stub, fully offline | $0, safest for the stage demo |
| `gemini` | Google Gemini Flash vision + local embeddings | $0 (free tier) |
| `aws` | Gemini vision + Amazon Rekognition (serial OCR + labels) + Bedrock Claude Haiku | low, needs AWS creds |
| `bedrock` / `anthropic` | Claude vision | paid |

Every call uses a 4-rung fallback ladder (live → cached → rule stub → review), so the
demo never blocks on a network call. Fingerprint embeddings run locally (Pillow and
numpy, no GPU, no model download).

## What is real vs mocked (the honesty rule)

| Capability | Status |
|---|---|
| Defect detection | REAL (Gemini Flash; Rekognition labels add support in `aws` mode) |
| Serial OCR | REAL (Gemini, or Amazon Rekognition DetectText in `aws` mode) |
| Fingerprint identity | REAL (local embedding + perceptual hash + serial) |
| Grading | REAL (deterministic rubric over AI-extracted defects) |
| Disposition routing | REAL (rules decide; AI rewords the explanation) |
| Buyer matching | REAL logic, SEEDED demand data |
| Carrier booking, payments | MOCKED behind real interfaces, badged in the ops dashboard |
| Delivery-time fingerprint capture | SEEDED (the courier captures it in production) |

The ops dashboard badges every mocked service. When a judge asks "what is live?", we
flip the dashboard. We never bluff.

## Repo structure

```
.
├── apps/
│   ├── api/    # FastAPI backend (event bus, custody ledger, SSE, AI layer, services)
│   └── web/    # React + Vite + Tailwind (seller, buyer, ops; Amazon-styled)
├── RELAY_AI_Masterplan.md   # strategy + architecture + demo script
├── HANDOUT.md               # living collaboration log (read before each session)
└── DEPLOY.md                # deployment guide
```

## Quickstart

```bash
# Backend
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # default mode is offline-safe "mock"
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd apps/web
npm install
npm run dev                 # http://localhost:5173
```

Backend runs fully offline in `mock` mode. For live AI, set `RELAY_AI_MODE=gemini`
and `RELAY_GEMINI_API_KEY` (free key at https://aistudio.google.com/apikey), using
model `gemini-2.5-flash-lite`. Smoke test: `.venv/bin/python apps/api/smoke_test.py`.

## Deploy

See `DEPLOY.md`. Short version: backend as a container on Render (or AWS App Runner
for the `aws` mode), frontend on Vercel with `VITE_API_BASE` pointed at the backend.

## Team

2 Peas in a Pod, Thapar University.
- Samarth Chatli, AI / CV and Frontend
- Udai Batta, Backend, Infra and DevOps
