# RELAY AI — *Returns That Never Return.*

**The trust and routing layer for reverse commerce.**
Built for **HackOn with Amazon · Season 6.0** · Theme: AI-Powered Returns and Sustainable Resale

**[Live Demo](https://amazonhackon-one.vercel.app)** · [Seller App](https://amazonhackon-one.vercel.app) · [Buyer Feed](https://amazonhackon-one.vercel.app/buyer) · [Ops Dashboard](https://amazonhackon-one.vercel.app/ops)

---

> *A pair of headphones is returned in Patiala.*
> *Trucked 1,800 km to a warehouse in Mumbai.*
> *Sits in a tote for three weeks.*
> *Inspected by a human for 90 seconds.*
> *Shipped 1,750 km back — to a buyer who lives 4 km from the original customer.*
>
> **3,500 km. To move 4.**
>
> Everyone in that supply chain knows this is insane. Nobody fixed it. Until now.

---

## The Insight

Every returns system on earth routes items through a warehouse for exactly one reason: **trust**. Nobody believes the customer's description of an item's condition, so the warehouse inspects, grades, and re-lists it.

The warehouse is a **$30-per-item trust machine.**

That trust machine is economically broken. Inbound shipping, manual inspection, storage, value decay across a 2–6 week loop, outbound shipping — **$25–40 in cost against items often worth $15–60.** The rational corporate response has become "keep it, here's your refund" — which trains fraud, fills landfills with an estimated 9.6 billion lbs of returned goods per year (Optoro), and writes off ~$743B in US merchandise annually (NRF, 2023).

Nobody attacks the root assumption: inspection must happen at a facility. That assumption was true in 2010. Multimodal AI made it false in 2024.

RELAY moves that trust machine to the doorstep. A guided AI inspection at the front door verifies the exact unit, grades its condition, screens for fraud, and routes it directly to a nearby buyer with a signed trust certificate. The item never has to go back.

**Returns become transfers. The item never touches a warehouse.**

---

## Demo

> **[Watch the demo video →](https://youtu.be/89pVGSbFN6c?si=X2AI7cxgYVGlauWG)**

Or run it yourself in two minutes — the demo is live and deployed.

### Three screens, one continuous story

| Route | Who | What |
| --- | --- | --- |
| [`/`](https://amazonhackon-one.vercel.app) | **Asha** (seller) | Orders → Guided scan → Fingerprint verify → Grade certificate → Buyer match → Journey reveal |
| [`/buyer`](https://amazonhackon-one.vercel.app/buyer) | **Rohan** (buyer) | Live demand feed · Reserve a verified item · Confirm delivery |
| [`/ops`](https://amazonhackon-one.vercel.app/ops) | Operations | Dark mission-control · Live event stream · REAL vs MOCK service registry |

### Run the full flow (2 minutes)

1. Open the [seller app](https://amazonhackon-one.vercel.app). Tap **Return or replace** on the JBL Tune 770NC.
2. Walk the guided scan — watch the AI redirect you to the correct view when you hold up the wrong angle.
3. See the **fingerprint match animate to 96.4% identity confidence** and the Grade B trust certificate mint with a QR code.
4. Flip the **"scan the swap unit"** toggle. Watch the fraud interrupt fire in red — serial SN-88412 ≠ delivered SN-77109 — caught in under four seconds.
5. Resume the honest path. Hit **Find a buyer nearby** and watch the live map draw a route to Rohan 4.27 km away.
6. Open [`/buyer`](https://amazonhackon-one.vercel.app/buyer) on a second tab and reserve from Rohan's side.
7. Hit the **journey screen**: 3,500 km and 2 warehouses vs 4.27 km and 0 warehouses. The item never touched a warehouse.
8. Open [`/ops`](https://amazonhackon-one.vercel.app/ops) — watch the live event feed tick as you run the flow. Every step logged, every service labeled REAL or MOCK, no bluffing.

> The backend runs on Render's free tier and may take ~30 s to wake from idle. The demo runs on a cached real Gemini pass over the actual JBL unit, so the stage path is instant and offline-safe regardless.

---

## How It Works

### The hero flow, step by step

```text
[Asha's door]  →  Guided AI scan  →  Fingerprint verify  →  Grade certificate
                                                                      ↓
[Rohan's door] ←  Local courier   ←  Buyer match + route  ←  Disposition engine

                    0 warehouses. 0 facility stops. Trust created at the door.
```

| Step | What happens | AI / Tech |
| --- | --- | --- |
| **1. Return initiated** | "Doorstep AI Return — verified in 3 minutes, picked up tomorrow" replaces the drop-off label | — |
| **2. Guided AI scan** | Camera sequences through required views; on-device blur/brightness/fill checks; AI redirects wrong angles in plain language | Client-side Laplacian + Gemini Flash vision |
| **3. Fingerprint identity** | Today's unit is matched against its delivery-day "birth certificate" — multimodal embedding, perceptual hash, and OCR'd serial — composite confidence displayed live | Local embedding + Rekognition DetectText / Gemini OCR |
| **4. Fraud screen** | Swap unit → serial mismatch → red interrupt → human review queue with full evidence bundle | Composite trust score + behavioral flags |
| **5. Grade certificate** | Vision model returns structured defect map; deterministic rubric converts to Grade A–D; QR-stamped trust certificate minted | Gemini Flash + severity-weighted rubric |
| **6. Disposition** | Rules engine decides: Grade B + 1 buyer 4.27 km away + resale ₹4,140 > liquidation → **DIRECT RELAY** | Rule engine + Bedrock Haiku (explanation) |
| **7. Buyer match** | Graded item matched to closest buyer by haversine distance, grade fit, and price headroom; route drawn on live map | Haversine ranking over demand waitlist |
| **8. Journey reveal** | Old world vs RELAY side by side. Km avoided. CO₂ avoided. The item never touched a warehouse. | — |

---

## Philosophy

**AI perceives. Rules decide.**

The vision model extracts structured observations — defect type, location, size, severity. A deterministic rubric, held in versioned config and not in the prompt, converts those observations into grades, prices, and routing decisions. Outcomes are consistent, auditable, and defensible across every SKU and every inspector.

A fraud interrupt never auto-accuses. It routes to human review with the full evidence bundle.

**AI flags. Humans accuse.**

---

## What Is Real vs Mocked

We never bluff. Every service is labeled in the ops dashboard. Here is the full picture:

| Capability | Status | Detail |
| --- | --- | --- |
| Defect detection | **REAL** | Gemini Flash vision with JSON-forced structured output; Rekognition DetectLabels corroborates in `aws` mode |
| Serial number OCR | **REAL** | Gemini OCR or Amazon Rekognition DetectText (`aws` mode); regex-validated serial extraction |
| Fingerprint identity | **REAL** | On-device color histogram + gradient orientation embedding, L2-normalised; cosine + pHash + serial composite |
| Condition grading | **REAL** | Deterministic severity-penalty rubric; confidence from mean defect confidence × product-match confidence |
| Trust / fraud scoring | **REAL** | Composite of fingerprint identity × serial × behavioral flags (return velocity, wardrobing window, reason consistency) |
| Disposition routing | **REAL** | Rule engine decides path; Bedrock Claude Haiku rewords the explanation for ops |
| Buyer matching | **REAL logic, seeded demand** | Haversine + grade-fit + price-headroom ranking; production = OpenSearch k-NN + geo |
| On-device quality gate | **REAL** | Laplacian variance (blur), mean luma (brightness), center-variance fill proxy — runs every frame |
| Live event stream | **REAL** | Server-Sent Events from an append-only custody ledger; ops dashboard subscribes live |
| Carrier booking | **MOCKED** | Behind a real interface; badged MOCK in ops; Shiprocket/Delhivery adapter is the production swap |
| Payments / refund ledger | **MOCKED** | Behind a real interface; badged MOCK in ops |
| Delivery-time fingerprint capture | **SEEDED** | In production the courier app captures this at delivery; seeded catalog data in the demo |

The ops dashboard at `/ops` shows this table live, with real-time REAL / MOCK / SEEDED / ROADMAP badges. When a judge asks "what's actually live?" — we flip the dashboard.

---

## AI Modes

One environment variable, four providers. Same prompts and schema work across all of them — perception is a stateless model call.

```sh
RELAY_AI_MODE=mock        # cached real-Gemini output, offline-safe, $0 — default for demo
RELAY_AI_MODE=gemini      # live Gemini Flash vision + local embeddings, free tier
RELAY_AI_MODE=aws         # Gemini vision + Amazon Rekognition (serial OCR + defect labels)
                          # + Bedrock Claude Haiku disposition prose — the Amazon-native stack
RELAY_AI_MODE=bedrock     # Claude Sonnet vision on Bedrock (full AWS)
RELAY_AI_MODE=anthropic   # Claude Sonnet direct API
```

The fallback ladder (every AI call):

```text
① Live model call  →  ② Cached real output for demo SKU  →  ③ Rule-based stub  →  ④ "Inspector review queued"
```

The demo never blocks on a network call. We pre-ran the real vision model on our actual JBL unit and cached the genuine output — so the stage run shows real AI, served reliably. Fingerprint embeddings run locally on Pillow and numpy; no GPU, no model download, no API cost.

---

## Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                         RELAY AI Core                            │
│                                                                  │
│  [Scan]──▶[Fingerprint]──▶[Defects]──▶[Grading]──▶[Pricing]    │
│                                                     │            │
│              [Fraud/Trust]◀────────────────────────┘            │
│                   │                                              │
│                   ▼                                              │
│             [Disposition]──▶[Matching]──▶[Carrier]              │
│                                                                  │
│  Every transition → EventBus → append-only custody ledger       │
│  Ops dashboard subscribes over SSE; certificate reads the log   │
└──────────────────────────────────────────────────────────────────┘
```

**The monolith is the production architecture with the network calls removed.**

Each in-process service module (`scan`, `fingerprint`, `defects`, `grading`, `pricing`, `fraud`, `matching`, `disposition`, `carrier`) has the same boundary as its target AWS counterpart. The swap is additive infrastructure, not a redesign:

| Today (demo) | Production swap |
| --- | --- |
| In-process FastAPI module | AWS Step Functions (resumable, human-in-the-loop return workflow) |
| In-process event bus | Amazon EventBridge + SQS + DLQs (decoupling and burst) |
| In-memory session store | DynamoDB single-table (sessions + events) |
| Local embedding + haversine | Amazon OpenSearch (k-NN fingerprint index + geo matching) |
| Gemini Flash vision | Amazon Bedrock Claude Sonnet / Titan Multimodal |
| Render container | AWS App Runner / Fargate |
| Seeded demand | Real buyer demand feed from the Amazon Renewed waitlist |

**Scaling in one sentence:** everything stateful is managed, everything compute is stateless behind queues — scale is a quota request, not a redesign, with near-zero idle cost that matches a post-holiday returns spike.

---

## Tech Stack

```text
Frontend    React 18 · Vite · TypeScript · Tailwind CSS · Framer Motion · React Leaflet
Backend     FastAPI · Pydantic v2 · Server-Sent Events · asyncio
AI          Google Gemini Flash · Amazon Rekognition · Bedrock Claude Haiku · local image embeddings (Pillow + NumPy)
Infra       Vercel (frontend) · Render (backend container) · Docker
```

---

## Run Locally

```bash
# 1. Backend
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # RELAY_AI_MODE=mock by default — fully offline
uvicorn main:app --reload --port 8000

# 2. Frontend (new terminal)
cd apps/web
npm install
npm run dev                    # http://localhost:5173
```

The backend runs fully offline in `mock` mode — no API keys needed, no network calls, demo-safe.

**To run with live AI:** set `RELAY_AI_MODE=gemini` and `RELAY_GEMINI_API_KEY` (free at [aistudio.google.com](https://aistudio.google.com/apikey)), model `gemini-2.5-flash-lite`.

**End-to-end smoke test:** `.venv/bin/python apps/api/smoke_test.py` — runs the full happy path, fraud path, buyer path, and ops check against the live server.

---

## The Business

RELAY is not a resale app. It is **infrastructure for reverse commerce** — a neutral trust and settlement rail that any retailer, marketplace, carrier, or insurer plugs into.

Wedge → platform, each rung profitable:

```text
[Day 1]  Fraud-screen + grading API for D2C brands (SaaS, no logistics needed)
    ↓
[Year 1] Doorstep grading → peer relay routing → carrier integration
    ↓
[Year 2] Trust certificates for resale marketplaces and insurers (Trust API)
    ↓
[Year 3] The UPI of second-life commerce — a neutral rail any platform settles on
```

**Three revenue layers:** per-verification SaaS fee · 5–10% relay take-rate on direct transfers · Trust API (certificates-as-a-service for platforms pricing returns risk).

**The moat compounds.** Every graded item emits a labeled tuple: photos → defects → grade → price → realized sale → dispute outcome. This is the only dataset in the world that closes the loop from image to realized second-life price — a pricing oracle no competitor can build without doing the work. Demand density is a local network effect: RELAY gets better in each city as it grows there, the moat shape of UPI and Uber-class platforms.

**Why Amazon, specifically.** Amazon already owns every ingredient: delivery-time photo capture (the fingerprint birth certificate), Amazon Renewed and Warehouse Deals (the resale demand side), the Flex network (last-mile relay capacity), and Bedrock/Rekognition (the AI layer). RELAY is the missing orchestration layer between assets Amazon already owns. At nine-figure return volumes, **$5 saved per return is a billion-dollar line item** — before counting fraud recovered and the ESG metrics (km eliminated, kg diverted from landfill) that are now board-level targets.

---

## Impact, Measured

Every completed relay logs real numbers:

- **Km of shipping avoided** — computed from actual seller and buyer coordinates
- **CO₂e avoided** — per km, per item category
- **Warehouse cost saved** — ~$30 per return eliminated
- **Fraud caught** — at the doorstep, before the item moves an inch
- **Items diverted from landfill** — trackable, reportable, board-ready

The ops dashboard shows these live. The journey screen shows them per return. Every number is derivable from real session data, not asserted.

---

## Team

### 2 Peas in a Pod · Thapar University

| Member | Role |
| --- | --- |
| **Samarth Chatli** | AI / computer vision · frontend architecture · demo design |
| **Udai Batta** | Backend · AWS integration · infra · DevOps |

HackOn with Amazon · Season 6.0

---

*"The warehouse is a trust machine. We moved trust to the doorstep.*
*Returns become transfers. The item never touches a warehouse."*

— RELAY AI
