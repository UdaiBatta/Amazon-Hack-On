# RELAY AI — Returns That Never Return

**The trust and routing layer for reverse commerce.**

🔗 **Live demo:** https://amazonhackon-one.vercel.app
📄 Built for **HackOn with Amazon, Season 6.0** · Theme: Second Life Commerce, AI-Powered Returns and Sustainable Resale

> A pair of headphones is returned in Patiala. It is trucked 1,800 km to a warehouse
> in Mumbai, sits for three weeks, is inspected for 90 seconds, then shipped 1,750 km
> back, to a buyer who lives 4 km from the original customer. 3,500 km, to move 4.
>
> Everyone in that supply chain knows it is insane. Nobody fixed it. Until now.

---

## The insight

Every returns system on earth routes items through a warehouse for one reason:
**trust**. Nobody believes the customer's description of an item's condition, so the
warehouse inspects, grades, and re-lists it. The warehouse is a **$30-per-item trust
machine**.

RELAY moves that trust machine to the doorstep. A guided AI inspection verifies the
exact unit, grades its condition, screens for fraud, and routes it straight to a
nearby buyer with a signed trust certificate. The day phones got good cameras and AI
got eyes, the warehouse became optional.

**Returns become transfers. The item never touches a warehouse.**

---

## Try it (2 minutes)

Open the [live demo](https://amazonhackon-one.vercel.app) and:

1. On the seller storefront, open the JBL order and tap **Return or replace**, then
   **Start Doorstep AI Return**.
2. Walk the guided scan, watch the AI redirect you on a wrong view, then see the
   **fingerprint match** and the **Grade B trust certificate**.
3. Flip the **"scan the swap unit"** toggle to trigger the live **fraud interrupt**.
4. Hit **Find a buyer nearby** to see the map route to Rohan 4.27 km away, and the
   final **journey screen**: 3,500 km vs 4.27 km, the item never touched a warehouse.
5. Open **`/ops`** for the live mission-control dashboard and **`/buyer`** for the
   buyer's demand feed.

> The backend runs on Render's free tier and sleeps when idle, so the first request
> may take ~30 seconds to wake. Best experienced on the cached demo path (`mock`
> mode), which serves real Gemini output captured on the actual demo unit.

---

## How it works (the hero flow)

| Step | What happens | Tech |
|---|---|---|
| **Doorstep return** | Asha taps Return and sees "Doorstep AI Return, verified in 3 minutes" instead of a drop-off label | — |
| **Guided scan** | The camera sequences her through each view, with on-device blur/brightness/fill checks and an AI that redirects a wrong angle | OpenCV-style heuristics + vision model |
| **Fingerprint check** | Today's unit is matched against its delivery-day "birth certificate" (embedding + perceptual hash + serial) | local embedding + Rekognition / Gemini OCR |
| **Fraud screen** | A swapped unit (different serial) trips a red interrupt in seconds and routes to human review | composite trust score |
| **Grade certificate** | A vision model finds defects; a deterministic rubric mints a Grade A to D certificate with a scannable QR | Gemini / Bedrock + rubric |
| **Disposition** | Rules decide the route (relay / liquidate / recycle); AI rewords the explanation on the ops dashboard | rule engine + Bedrock Haiku |
| **Buyer match** | The graded item is matched to the closest waiting buyer and routed door to door | haversine over demand waitlist |
| **Journey reveal** | 3,500 km and 2 warehouses vs 4.27 km and 0 warehouses | — |

## The three surfaces

| Route | Who | What |
|---|---|---|
| `/` | Seller (Asha) | Amazon-style orders, guided scan, certificate, fraud screen, match map, journey |
| `/buyer` | Buyer (Rohan) | Live demand feed, reserve a verified item, confirm on delivery |
| `/ops` | Operations | Dark mission-control: live event stream, REAL vs MOCK registry, impact metrics |

---

## Philosophy: AI perceives, rules decide

The vision model extracts structured defects and reads the serial. A deterministic
rubric (in config, not in the prompt) turns that into a grade, a price, and a routing
decision, so outcomes are consistent, auditable, and defensible. A fraud interrupt
never auto-accuses; it routes to human review with the full evidence bundle.
**AI flags, humans accuse.**

## AI modes (one switch, four providers)

Set `RELAY_AI_MODE` in `apps/api/.env`:

| Mode | Perception | Cost |
|---|---|---|
| `mock` | cached / stub, fully offline | $0, safest for the stage demo |
| `gemini` | Google Gemini Flash vision + local embeddings | $0 (free tier) |
| `aws` | Gemini vision + Amazon Rekognition (serial OCR + labels) + Bedrock Claude Haiku | low, needs AWS creds |
| `bedrock` / `anthropic` | Claude vision | paid |

Every call uses a 4-rung fallback ladder (live → cached → rule stub → review), so the
demo never blocks on a network call. The same pipeline runs free on Gemini today or
natively on Amazon Rekognition and Bedrock by flipping one variable. Fingerprint
embeddings run locally (Pillow and numpy, no GPU, no model download).

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

---

## Architecture

An event-driven FastAPI core whose in-process service modules (`scan`, `fingerprint`,
`defects`, `grading`, `pricing`, `fraud`, `matching`, `disposition`) share the exact
boundaries of the target AWS system. Every state change emits an event onto a bus and
appends to an append-only custody ledger; the ops dashboard subscribes over a live SSE
stream. **The monolith is the production architecture with the network calls removed.**

The production path is a swap, not a rewrite: Step Functions (the resumable return
workflow), EventBridge + SQS (decoupling and burst), DynamoDB (sessions and events),
OpenSearch (k-NN fingerprint index + geo matching), S3 + CloudFront (media), and
Bedrock + Titan (perception). Everything stateful is managed and everything compute is
stateless behind queues, so scaling is a quota request, not a redesign.

## Tech stack

- **Frontend:** React, Vite, TypeScript, Tailwind, Framer Motion, Leaflet (Amazon-styled)
- **Backend:** FastAPI, Pydantic, Server-Sent Events
- **AI:** Gemini Flash, Amazon Rekognition, Bedrock Claude Haiku, local image embeddings
- **Deploy:** Vercel (frontend) + Render (backend container); AWS App Runner for `aws` mode

---

## Run locally

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

Backend runs fully offline in `mock` mode. For live AI, set `RELAY_AI_MODE=gemini` and
`RELAY_GEMINI_API_KEY` (free key at https://aistudio.google.com/apikey), model
`gemini-2.5-flash-lite`. Smoke test: `.venv/bin/python apps/api/smoke_test.py`.

## Deploy

See `DEPLOY.md`. Frontend on Vercel (root `apps/web`, set `VITE_API_BASE` to the
backend URL), backend as a container on Render (root `apps/api`), or AWS App Runner
for the `aws` mode.

## Demo

- **Live app:** https://amazonhackon-one.vercel.app
- **Video script:** `RELAY_Demo_Script.md` (4m30s, shot by shot)
- **Demo video:** to be added

---

## Team

**2 Peas in a Pod**, Thapar University.
- **Samarth Chatli** — AI / CV and Frontend
- **Udai Batta** — Backend, Infra and DevOps

*RELAY AI · HackOn with Amazon Season 6.0*
