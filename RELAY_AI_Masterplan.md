# RELAY AI — The Masterplan
### "Returns That Never Return."

> **The moneyshot:** *"The item never touched a warehouse."*

This document is the build blueprint, the architecture review, and the demo script — all in one. It is written to be handed directly to Claude/Codex for code generation, to your designer for UI, and to your presenter for slides. Every section ends in decisions, not options.

**One honesty rule up front (it will win you Q&A):** mock aggressively, but never lie to a judge. When asked "is this real?", the winning answer is: *"The grading and fingerprint matching are live AI calls. The carrier label API is mocked — here's the production integration on slide 14."* Judges reward teams who know exactly where their demo ends and production begins. Teams who get caught bluffing lose instantly.

---

# SECTION 1 — PRODUCT STRATEGY

## 1.1 What RELAY actually is

RELAY is **not a resale marketplace**. It is a **trust and routing layer for reverse commerce** — the infrastructure that makes it safe to ship a returned item from Customer A directly to Buyer B without a warehouse ever inspecting it.

The warehouse exists in the returns loop for exactly one reason: **nobody trusts the customer's description of the item's condition.** The warehouse is a $30-per-item trust machine. RELAY replaces that trust machine with AI: doorstep multimodal inspection, product fingerprinting against a delivery-time "birth certificate," and an auditable AI grading certificate. Once trust is established at the doorstep, the item can be routed point-to-point.

**One sentence for judges:** *"Every returns system in the world routes items through a warehouse because that's where trust is created. RELAY creates trust at the doorstep — so the item never has to go back."*

## 1.2 Why this problem matters globally

- Retail returns in the US alone are estimated at **$700B+ in merchandise annually** (NRF has reported ~$743B for 2023 — verify the latest figure before your slide, and cite the source on-slide).
- Processing a single return is commonly estimated at **$25–35 in reverse logistics cost**, and for low-ASP items can consume **a majority of the item's value** — which is why retailers increasingly tell customers "keep it, here's your refund."
- An estimated **billions of kilograms of returned goods go to landfill every year** because inspection + restocking costs more than the item is worth. (Optoro's widely cited figure: ~9.6 billion lbs/year in the US.)
- E-commerce return rates run **2–3× higher than brick-and-mortar** (apparel often 20–30%), and they grow every year as e-commerce share grows.

The dirty secret: the warehouse round-trip means a returned item often travels **2,000+ km and waits 2–6 weeks** before it can be resold — by which time fashion items are off-season, electronics have dropped a price tier, and the resale value has decayed 20–40%.

## 1.3 Why current systems fail

Every existing player optimizes a *segment* of the broken pipeline instead of deleting it:

| Player | What they do | Why it fails |
|---|---|---|
| Retailer returns desks | Refund + restock | Warehouse-bound; cost center; weeks of latency |
| Liquidators (B-Stock, Liquidity Services) | Bulk-sell pallets at 10–20¢/$ | Value destruction by design |
| Resale marketplaces (eBay, OLX, Poshmark) | Peer listings | Trust burden on buyer; no verification; fraud-rich |
| Returns SaaS (Loop, Narvar, Happy Returns) | Better return *UX* | Item still goes to a warehouse |
| "Returnless refunds" | Skip logistics entirely | Pure write-off; trains fraud; landfill |

Nobody attacks the root assumption: **inspection must happen at a facility.** That assumption was true in 2010. Multimodal AI made it false in 2024. RELAY is the first system designed for the post-assumption world.

## 1.4 Why warehouse dependency is broken (the economics)

The warehouse round trip stacks five costs on a single item: inbound shipping (~$8–12), receiving + manual inspection labor (~$5–10), storage + handling, value decay during the 2–6 week loop, and outbound shipping again to the next buyer. Total: frequently **$25–40 against an item whose resale value may be $15–60.** The unit economics are upside-down, which is why the rational corporate response has been "throw it away or refund without return" — an answer that is economically and environmentally absurd.

RELAY's economics: one local shipment (customer → nearby buyer, often <50 km), zero warehouse labor, zero storage, near-zero value decay. The cost structure collapses from ~$30 to roughly the cost of a local parcel plus pennies of AI inference.

## 1.5 Why this beats generic resale platforms

A resale marketplace creates a *second* transaction with all the friction of the first. RELAY makes the return **be** the resale. The customer doesn't list anything, photograph for a listing, negotiate, or wait. The buyer doesn't gamble on a stranger's photos — they get an AI-graded, fingerprint-verified, fraud-screened item with a trust certificate. The retailer doesn't lose the item into a third-party ecosystem — they keep the transaction, the data, and the margin.

Marketplaces compete on inventory. **RELAY competes on trust per item.** That's a different, deeper moat.

## 1.6 Why Amazon would care

1. Amazon processes hundreds of millions of returns per year; even a $5/item saving is a billion-dollar line item.
2. Amazon already has the raw ingredients RELAY needs: delivery-photo capture (the "birth certificate" fingerprint), Warehouse Deals / Amazon Renewed (the resale demand side), Flex drivers (last-mile relay capacity), and Rekognition/Bedrock (the AI layer). RELAY is the missing orchestration layer between assets Amazon already owns.
3. Returns fraud (item swapping, brick-in-box, wardrobing) costs retailers an estimated **$80–100B+ annually** in the US (NRF estimates ~13–15% of returns are fraudulent — verify before slide). RELAY's fingerprinting attacks this directly.
4. Sustainability reporting pressure: "returns diverted from landfill, km of shipping eliminated" is a metric Amazon's ESG team would kill for.

## 1.7 The emotional storytelling angle

The judge-memory hook is **the absurd journey of one object.** Open with it:

> *"This pair of headphones was returned in Patiala. It was trucked 1,800 km to a warehouse in Mumbai, sat in a tote for three weeks, was inspected by a human for 90 seconds, repackaged, and shipped 1,750 km back — to a buyer who lives 4 km from the original customer. The item travelled 3,500 km to move 4 kilometres."*

That's the emotional peak: **the system is insane, and everyone in the room instantly knows it.** Then the inevitability frame: "Inspection moved to the doorstep the day phones got good cameras and AI got eyes. We're just the first team to build it." Inevitability is the most powerful judge emotion — it converts "cute hack" into "I'm watching the future early."

## 1.8 Why this is a startup, not a hack

- Wedge: returns fraud detection SaaS for D2C brands (sellable on day one, no logistics needed).
- Expansion: doorstep grading → peer routing → full reverse-commerce OS.
- Moat: every graded item builds a proprietary dataset of (photos → defects → grade → realized resale price → dispute outcome). That dataset is the pricing oracle for the entire second-life economy. Nobody else can build it without doing the work.
- Endgame: RELAY as **the UPI of second-life commerce** — a neutral trust + settlement rail any retailer, marketplace, or carrier plugs into. Rails businesses are the billion-dollar shape.

---

# SECTION 2 — THE FULL USER FLOW

Three actors: **Seller-Customer (Asha)** returning an item, **Buyer (Rohan)** on the demand waitlist, **RELAY brain** in the middle. Eleven steps. For each: backend, frontend, AI, data, and the wow-beat.

### Step 1 — Return initiation
- **User sees:** Their order list (mock Amazon-style). Taps "Return" on item → reason picker → instead of "print label, drive to drop-off," screen says: **"New: Doorstep AI Return — verified in 3 minutes, picked up tomorrow."**
- **Backend:** `POST /returns` creates a `ReturnSession` (DynamoDB) with item metadata, original order ID, and crucially the **fingerprint reference** captured at delivery time. Emits `return.initiated` event.
- **AI:** None yet. (Production: return-reason NLP to pre-route obvious cases.)
- **Wow-beat:** The framing itself. "Your return starts at your door, not at a warehouse."

### Step 2 — AI-guided scanning
- **User sees:** A camera flow that *talks back*. An overlay outline of the product, with sequenced prompts: "Show the front… now the serial number sticker… tilt to catch the screen under light… closer on the left hinge." A progress ring fills as required views are captured.
- **Backend:** Each frame → `POST /sessions/{id}/frames` → S3 (presigned upload). A per-category **capture checklist** (JSON config) drives the sequence. Step Functions (or in-MVP, a FastAPI state machine) tracks checklist completion.
- **AI:** Two layers. (a) Cheap real-time heuristics client-side: blur detection (Laplacian variance), brightness check, "object fills ≥40% of frame" — all doable in JS/OpenCV in an hour and feel magically responsive. (b) Per-captured-frame, a Claude vision call verifies "is this actually the serial label?" and can reject with a natural-language redirect: *"That's the box barcode — I need the sticker under the left earcup."* That sentence alone will get a gasp.
- **Data generated:** 6–10 keyed images per session (front/back/serial/defect-closeups), quality scores, capture timestamps.
- **Wow-beat:** The AI *redirecting* the human mid-scan. Guided capture is the single most demo-visible AI moment — invest polish here.

### Step 3 — Product fingerprint verification
- **User sees:** "Verifying this is the exact unit we delivered…" → animated comparison: delivery-day photo on left, today's photo on right, match score counting up → **"✓ Identity confirmed — 96.4% fingerprint match."**
- **Backend:** Pulls the stored fingerprint record (created at delivery: image embedding + serial OCR + pHash). Computes: cosine similarity of multimodal embeddings (Bedrock Titan Multimodal or CLIP), perceptual-hash distance, and exact-match on OCR'd serial (Claude vision or Textract). Weighted composite → `identity_confidence`.
- **AI:** Embedding similarity is **real and easy** — this is the highest credibility-per-hour feature in the project.
- **Data:** `FingerprintMatch{embedding_sim, phash_dist, serial_match, composite, verdict}`.
- **Wow-beat:** Side-by-side photo morph with the score animating. Looks like CSI, is actually 30 lines of numpy.

### Step 4 — Defect detection
- **User sees:** Their photos with **bounding-box style defect callouts**: "Scuff, left earcup, 2cm, cosmetic — minor." Each defect carded with severity chip.
- **Backend:** All session images → one structured Claude (Sonnet on Bedrock) vision call with a strict JSON schema: `defects[{type, location, size_estimate, severity, affects_function}]`. Store on session.
- **AI:** 100% real. Claude vision on consumer goods defects is genuinely strong. Prompt it with the product's catalog images as the "expected condition" anchor.
- **Wow-beat:** Specificity. "Scratch on lower-left of screen, ~3cm, does not cross active display area" reads like an expert inspector, because it is one.

### Step 5 — Condition grading
- **User sees:** A **Grade Certificate** materialize: big letter grade (A/B/C/D), defect summary, confidence %, certificate ID, QR code, timestamp. Designed like a PSA card-grading slab — collectible-looking.
- **Backend:** Deterministic rubric over the defect list (severity-weighted scoring → grade bands) so grades are *consistent and defensible*, with Claude generating the human-readable rationale. Rubric in config, not in the prompt — say this in Q&A, judges love "AI perceives, rules decide."
- **Wow-beat:** The certificate artifact itself. Make it beautiful; it's your trust totem and it appears in three more demo moments.

### Step 6 — Pricing
- **User sees:** "Resale value: ₹4,150 (83% of current new price). Instant refund: ₹3,900." A small sparkline: "items like this sell within 2 days in your area."
- **Backend:** `price = base_price × grade_multiplier × category_decay(age) × local_demand_factor`. Seed a small comps table. Claude writes the one-line pricing rationale.
- **AI:** Heuristic engine presented honestly as "v1 pricing model; production = gradient-boosted model on realized sales." Don't fake an ML model that doesn't exist — the heuristic + rationale is impressive enough.

### Step 7 — Fraud detection (the planted demo moment — see Section 7)
- **User sees (happy path):** A quiet green "Fraud screen passed" chip. **(Fraud path):** full red interrupt: "⚠ Identity mismatch — the serial number on this unit (SN-88412) does not match the delivered unit (SN-77109). This return cannot proceed automatically."
- **Backend:** Composite trust score = fingerprint match × serial match × behavioral flags (return frequency, time-since-delivery, reason/defect consistency). Below threshold → route to `manual_review` queue.
- **Wow-beat:** Catching a *live swap attempt on stage*. This is your standing-ovation moment.

### Step 8 — Smart routing (disposition)
- **User sees:** Nothing — this is the brain working. Judges see it on the ops dashboard: a decision card — "Grade B + buyer demand within 6 km + resale value ₹4,150 > liquidation ₹900 → **DIRECT RELAY**."
- **Backend:** Policy engine: Grade A/B + nearby demand → relay; Grade C → liquidation channel; Grade D / fraud-flag → recycle/review. Emit `disposition.decided`. Have Claude generate the *explanation* of the decision for the dashboard — explainable routing is an architecture-points magnet.

### Step 9 — Buyer matching
- **User sees (buyer side):** Rohan, who wishlisted "these headphones, used-good, under ₹4,500," gets a push card: "Found: Grade B, verified, 4.2 km away, ₹4,150 — with AI inspection certificate. Reserve?"
- **Backend:** Demand waitlist table keyed by (product, max_price, geo). Haversine query over seeded buyers; rank by distance × price fit × wait time. (Production: OpenSearch geo + vector similarity for "similar item" matching.)
- **Wow-beat:** **The map.** Seller pin, pulsing demand pins around it, a line snapping to the matched buyer with "4.2 km" on it. This is the visual proof of the whole thesis.

### Step 10 — Shipment orchestration
- **User sees:** "Pickup scheduled tomorrow 10–12. Courier carries a tamper-evident RELAY bag." Generated shipping label with QR linking to the certificate.
- **Backend:** Mocked carrier adapter behind a real interface (`CarrierService.book()` returns a fake-but-well-formed booking). Production slide: Shiprocket/Delhivery/UPS APIs.

### Step 11 — Final transfer confirmation
- **User sees:** Buyer scans the QR on arrival → certificate opens → "Confirm received as described" → seller's refund finalizes, buyer's payment releases. Both see the item's **journey map: 4.2 km, 1 hop, 0 warehouses** vs. the ghosted "old world" route: 3,500 km, 2 warehouses, 19 days.
- **Wow-beat:** The journey comparison graphic IS the moneyshot line, rendered. End the demo on this screen.

---

# SECTION 3 — AI SYSTEM DESIGN

## 3.1 Model selection (decisive picks)

> **Provider decision (cost — added Session 3, 2026-06-13):** to keep the build
> **$0 and self-serviceable**, the hackathon-real vision provider is **Google
> Gemini Flash (free tier)** for defect detection, serial OCR, and frame
> validation, and a **local, on-device perceptual embedding** (`services/embeddings.py`,
> Pillow+numpy — no GPU, no download) for fingerprint identity. **Live key is
> configured (Session 3).** Working model = **`gemini-2.5-flash`** (note:
> `gemini-2.0-flash` had 0 free-tier quota on this project). Per-frame scan
> validation is kept on the fast on-device path (Gemini reserved for the
> high-value grade-time call) so the scan stays snappy. Bedrock Claude + Titan
> remain the **target/production** picks and the architecture is provider-agnostic
> (one-line swap). Honest line for judges: *"perception is a free-tier Gemini call
> today, a one-line swap to Bedrock/Titan in production — the architecture doesn't
> change."* Carrier/payments mocks unchanged.

| Capability | Model / tech | Real or mocked in 48h |
|---|---|---|
| Defect detection + scan validation | **Claude Sonnet (vision) on Bedrock**, structured JSON output | **REAL** — core of the project |
| Guided-scan live feedback | Client-side OpenCV heuristics (blur/brightness/fill) + per-frame Claude check | **REAL** (heuristics) + REAL (frame check) |
| Fingerprint identity | **Titan Multimodal Embeddings (or open CLIP)** cosine sim + pHash + serial OCR via Claude vision | **REAL** — embarrassingly easy, looks like deep tech |
| Micro-texture "FiberPrint" | Story only | **MOCKED** — show as roadmap, never claim live |
| Grading | Deterministic rubric over Claude-extracted defects | **REAL** |
| Pricing | Heuristic formula + comps table + Claude rationale | **REAL (heuristic)** — labeled as v1 model |
| Buyer matching | Haversine over seeded waitlist | **REAL** logic, **SEEDED** data |
| Disposition routing | Rule engine + Claude-generated explanation | **REAL** |
| Fraud behavioral signals | 3–4 hardcoded features into trust score | **SIMPLIFIED** |

## 3.2 The inference pipeline (one diagram to build)

```
frames → S3 ─→ [Quality Gate: blur/brightness] ─→ [Frame Validator: Claude "is this the requested view?"]
                                                        │
        ┌───────────────────────────────────────────────┤ (session complete)
        ▼                                               ▼
[Fingerprint Service]                          [Defect Extractor]
 embeddings + pHash + serial OCR                Claude vision → defects JSON
        │                                               │
        ▼                                               ▼
 identity_confidence ──────────────► [Trust Scorer] ◄── grade (rubric)
                                          │
                                          ▼
                              [Disposition Engine] → relay / liquidate / recycle / review
                                          │
                                          ▼
                                 [Matcher] → buyer → [Carrier (mock)] → certificate finalized
```

## 3.3 Structured-output contract (build this first — everything hangs off it)

```json
// Claude defect-extraction response schema
{
  "is_requested_view": true,
  "product_match": {"matches_catalog": true, "confidence": 0.93},
  "serial_number": {"detected": "SN-77109", "confidence": 0.98},
  "defects": [
    {"type": "scratch", "location": "left earcup, lower edge", "size_cm": 2.1,
     "severity": "minor", "affects_function": false, "confidence": 0.87}
  ],
  "overall_condition_notes": "Light cosmetic wear consistent with <30 days use."
}
```

Force this with a tool-use/JSON schema. Retry-with-repair on parse failure (one retry, then degrade gracefully — see 3.5).

## 3.4 Hackathon optimizations ("illusion engineering," done honestly)

- **Pre-warm everything.** Bedrock cold calls during a demo are death. Fire a dummy inference on app start and every 60s.
- **Cache the happy path.** Your demo product's photos should be pre-run; live calls happen, but a cached identical result stands behind them. If the live call is slow, the UI shows the cached result at the 4-second mark regardless ("optimistic resolve").
- **Constrain the universe.** Support exactly 2–3 product SKUs (headphones, a shoe, a small appliance). Per-SKU capture checklists and catalog anchor images make Claude's accuracy *dramatically* better than a general system — and judges only ever see those SKUs.
- **Latency theater.** Don't hide 5s of inference behind a spinner — narrate it: "Analyzing 8 angles… comparing against delivery fingerprint… checking 14 defect classes." Streaming status text makes latency feel like depth.
- **Confidence everywhere.** Every AI output displays a confidence %. It costs nothing and triples perceived rigor.
- **The honest mock pattern.** Mocked services live behind real interfaces with a `MOCK` badge visible in your *ops* dashboard (not the consumer UI). When a judge leans in and asks, you flip the dashboard and show exactly what's live vs mocked. This move has won hackathons by itself.

## 3.5 Fallback ladder (if AI fails live)

1. Live Bedrock call (timeout 6s) →
2. Cached response for the demo SKU (identical schema) →
3. Local rule-based stub (serial regex + canned defects) →
4. "Inspector review queued" graceful state (never an error screen).

Demo never blocks on a network call. Rehearse with WiFi off once.

---

# SECTION 4 — FRAUD & TRUST SYSTEM

This is your differentiation backbone. Most teams will demo resale; you will demo **trust infrastructure.**

## 4.1 The fingerprint: a "birth certificate" for every delivered item

At delivery (in production: the courier's existing delivery photo + a 2-second package scan), RELAY captures:

1. **Visual embedding** — multimodal embedding of the item/packaging (Titan/CLIP).
2. **Perceptual hash** — pHash of key views; robust to lighting, sensitive to substitution.
3. **Serial/identifier OCR** — exact-match anchor.
4. **(Roadmap) FiberPrint** — macro photo of a random surface patch; micro-texture is unique per unit like a fingerprint. *Story/roadmap only in 48h* — but it's a real research area (e.g., surface-texture authentication), so it survives Q&A.

At return, the same captures are recomputed and compared:

```
identity_confidence = 0.45·serial_exact + 0.35·embedding_cosine + 0.20·(1 − phash_dist_norm)
≥0.85 auto-pass · 0.60–0.85 extra-angle request · <0.60 fraud interrupt → human review
```

## 4.2 Anti-swap logic & edge cases (have these answers ready)

- **Swap (different unit, same model):** serial mismatch catches it — your demo moment.
- **Serial sticker removed:** "sticker absent" is itself a flag → embedding-only path with raised threshold → likely manual review. *Honest answer: this is the hard case; production adds FiberPrint + weight check at pickup.*
- **Brick-in-box:** courier scan at pickup (weight + one photo) is the production control; in demo, the buyer-confirmation step is the backstop.
- **Wardrobing (use-and-return):** defect/wear detection vs days-since-delivery; "wear inconsistent with claimed unopened" flag.
- **Photos of photos / replayed images:** mention EXIF + liveness (slight camera motion required between frames) as production controls.
- **AI is wrong, honest customer flagged:** every fraud interrupt routes to **human review with the full evidence bundle** — never an auto-accusation. Say the phrase "AI flags, humans accuse" in Q&A; it defuses the scariest ethical question instantly.

## 4.3 Chain of custody

Every state transition (delivered → scanned → graded → picked-up → delivered-to-buyer → confirmed) is an append-only event with actor, timestamp, geohash, and media refs — a custody ledger rendered as a timeline on the certificate. **Do not say "blockchain."** Say "append-only audit log; a chain where it earns its cost is a later decision." Judges are tired of blockchain; restraint reads as seniority.

## 4.4 The Trust Certificate (your product's icon)

One artifact carrying: grade, defect map thumbnails, identity confidence, fraud-screen status, custody timeline, certificate ID + QR. It is shown to the seller (step 5), the buyer (step 9), on the shipping label (step 10), and at handoff (step 11). One object, four appearances — that repetition is what makes judges *remember* the trust layer.

---

# SECTION 5 — SYSTEM ARCHITECTURE

Two architectures, deliberately: the **Target Architecture** (what you put on the slide and defend in Q&A) and the **48-Hour Build** (what actually runs). Presenting both, explicitly labeled, is itself an architecture-maturity signal.

## 5.1 Target architecture (the slide)

```
                         ┌──────────── CloudFront + S3 (web) ────────────┐
 Mobile/Web (React) ────►│  API Gateway ── Cognito (auth)                │
                         └───────┬───────────────────────────────────────┘
                                 ▼
                        ┌─ Return Orchestrator ─┐
                        │   AWS Step Functions   │   ← one state machine per ReturnSession
                        └──┬────────┬────────┬───┘
            (events via EventBridge; work via SQS; DLQs everywhere)
               ▼            ▼            ▼            ▼
        Scan Service   Fingerprint   Grading Svc   Disposition Svc
        (Lambda)       Service       (Lambda+      (Lambda rules
        S3 media in,   (Lambda →     Bedrock        engine + Bedrock
        quality gate   Titan embeds, Claude         explanation)
                       OpenSearch    vision)             │
                       k-NN index)                       ▼
                                                  Matching Service
                                                  (OpenSearch geo +
                                                   demand waitlist)
                                                         │
        DynamoDB (sessions/items/users/events)           ▼
        S3 (media, certificates)                  Carrier Adapter
        OpenSearch (vectors + geo)                (3P shipping APIs)
        CloudWatch + X-Ray (observability)
```

**Why each service (the Q&A ammo):**
- **Step Functions** — a return is a long-lived, resumable, human-in-the-loop workflow (scan can pause for hours; fraud can branch to review). Express workflows for the inference fan-out, Standard for the session. Built-in retries/timeouts = resilience for free.
- **EventBridge** — `return.initiated`, `scan.completed`, `fraud.flagged`, `disposition.decided`, `transfer.confirmed` as first-class events lets fraud analytics, notifications, and the ops dashboard subscribe without coupling. This is what lets RELAY later become a *platform* (partners subscribe to events).
- **SQS + DLQs** — Bedrock throttles and image processing spikes; queues absorb burst, DLQs make failures debuggable, idempotency keys on consumers.
- **Bedrock** — managed Claude vision + Titan embeddings; no GPU ops in week one; private inference for retail partners is the enterprise story.
- **DynamoDB** — session/event access patterns are key-value with high write bursts; single-table design with `PK=SESSION#id`.
- **OpenSearch** — one engine does both jobs: k-NN vector index for fingerprints and geo queries for buyer matching.
- **S3 + CloudFront** — media-heavy workload; presigned uploads keep images off your API path entirely.
- **SageMaker (roadmap)** — where the proprietary grading/pricing models train once you have real outcome data; the *data flywheel* slide.
- **Scaling logic in one line:** everything stateful is managed (DynamoDB/S3/OpenSearch), everything compute is stateless (Lambda) behind queues — so scale is a quota request, not a redesign. Cost: pay-per-return, ~zero idle cost — matches a returns workload that spikes after holidays.

## 5.2 The 48-hour build (what actually runs)

```
React (Vite + Tailwind) ── FastAPI monolith (single ECS/EC2/Fly box)
                              ├── /sessions /frames /verify /grade /match /ship
                              ├── modular services in-process (scan.py, fingerprint.py,
                              │    grading.py, pricing.py, matching.py, carrier_mock.py)
                              ├── boto3 → Bedrock (Claude Sonnet vision, Titan embeds)
                              ├── S3 (media) + DynamoDB (or SQLite if AWS fights you)
                              └── numpy cosine sim (skip OpenSearch; <100 vectors)
```

Same module boundaries as the target architecture — the monolith is the target system with the network calls removed. Say exactly that sentence to judges. FastAPI over Django here: you want async Bedrock calls, websockets for live scan feedback, and zero ORM ceremony; it plays to your existing Python strength without Django's weight.

## 5.3 Event & data lifecycle

Every state change appends to an `events` list (the custody ledger) AND updates session state. One write path, two read models: the consumer app reads state; the ops dashboard and certificate read the event log. This is "CQRS-lite" — name it in Q&A only if asked.

Media lifecycle: presigned PUT → S3 `raw/` → processed thumbnails → referenced by certificate → (production) lifecycle policy to Glacier after dispute window.

---

# SECTION 6 — HACKATHON MVP STRATEGY (48 HOURS)

## 6.1 Scope verdicts

**MUST BUILD (the demo spine):**
1. Guided scan flow with live feedback (the wow engine)
2. Real Claude defect detection + structured output
3. Real fingerprint match (embeddings + serial OCR) with the side-by-side UI
4. Grade Certificate (beautiful)
5. Fraud interrupt path (the planted moment)
6. Buyer match map + buyer-side reserve card
7. Journey comparison screen (4 km vs 3,500 km)
8. Ops dashboard showing events/decisions (architecture made visible)

**MOCK:** carrier booking, payments/refund ledger, notifications (in-app only), delivery-time fingerprint capture (pre-seeded for demo SKUs — *explained honestly as "captured by the courier at delivery; here's the seeded record"*).

**HARDCODE:** product catalog (3 SKUs), buyer waitlist (~12 seeded buyers around your demo city), pricing comps table, grading rubric weights.

**DO NOT BUILD (overengineering traps):** auth flows (one hardcoded user per role), real Step Functions, OpenSearch, microservice deployment, admin CRUD, chat/negotiation, payments, more than 3 SKUs, native mobile app (responsive web in a phone frame is indistinguishable on stage).

## 6.2 Team roles (4 people)

| Role | Owner profile | Owns |
|---|---|---|
| **AI Pipeline** | Strongest Python/Bedrock person (Udai — this is your PyTorch/AWS lane) | Prompts, JSON schemas, fingerprint math, grading rubric, fallback ladder, latency |
| **Backend/Infra** | Python/API person | FastAPI, S3/Dynamo, session state machine, seed data, deploy |
| **Frontend** | React person | Scan UX, certificate, map, dashboard, animations |
| **Story/Design/Demo** | Best presenter | Slides, script, props, rehearsal direction, judge Q&A bank — full-time from hour 0, not "whoever's free at the end" |

## 6.3 48-hour roadmap

| Block | Goal | Exit criterion |
|---|---|---|
| H0–2 | Repo, deploy skeleton, Bedrock hello-world vision call, demo SKUs photographed (good + "swap" unit) | A real Claude vision response in the repo |
| H2–8 | Backend session API + S3 upload; defect-extraction prompt iterated on real photos; frontend scan-flow shell | End-to-end: photo in → defects JSON out |
| H8–16 | Fingerprint service (embeds + pHash + OCR); grading rubric; certificate UI v1; seeded buyers + match logic | Identity match score renders in UI |
| H16–24 | Fraud interrupt path; ops dashboard events; map UI; pricing | **Full happy-path runs end-to-end (the real deadline)** |
| H24–32 | Polish pass: animations, latency theater, copywriting; fallback ladder + caching; buyer-side flow | Demo runs with WiFi off (fallbacks) |
| H32–40 | Slides + script; 3 full rehearsals incl. the fraud swap; record a backup screen-capture of the perfect run | Backup video exists |
| H40–48 | Freeze features. Bug-fix only. 2 more rehearsals. Sleep ≥4h. | Nobody touches `main` after H44 |

**Risk plan:** Bedrock access delayed → Anthropic API direct (same prompts). Vision accuracy disappointing on a SKU → swap the SKU, not the model (choose photogenic, defect-visible products: matte headphones > glossy black electronics). Live demo fails → narrated backup video *with the live system as the "and it's running right here" close*.

---

# SECTION 7 — DEMO & PRESENTATION STRATEGY

## 7.1 The 6-minute script

**[0:00 Hook]** Hold up the physical headphones. *"I bought these online. They're great — but I'm returning them. Watch what the system I'm about to show does NOT do: it does not send them to a warehouse."* (Stakes set in 12 seconds.)

**[0:30 Problem]** The absurd-journey map (Section 1.7), three brutal stats, one line: *"The warehouse isn't a logistics step. It's a trust step. So we moved trust to the doorstep."*

**[1:15 Live demo — happy path]** Phone on camera/mirror. Guided scan with the AI redirecting you once ("That's the box barcode — show me the sticker under the earcup"). Fingerprint match animation. Defect callouts. Certificate mints. *Let the room read the certificate in silence for two beats.*

**[3:00 The fraud moment]** *"Now — what if I try to cheat?"* Pull the second, older unit from under the table. Scan it. Red interrupt: serial mismatch. Pause. *"That's a ₹100-billion fraud problem, caught in four seconds at a doorstep."* (This is your applause line — earned, not begged.)

**[3:45 The match]** Buyer map reveal: pin 4.2 km away. Cut to buyer phone: reserve card → reserved. Mock pickup label prints/displays with the QR.

**[4:30 The moneyshot]** Journey-comparison screen. *"Old world: 3,500 kilometres, two warehouses, 19 days. RELAY: 4.2 kilometres, one courier, tomorrow. The item never touched a warehouse."* Hold the slide.

**[5:00 Architecture, 45 seconds]** One slide, target architecture, three sentences: event-driven, Step Functions as the return brain, Bedrock for perception, "the monolith we built this weekend has the same module boundaries — here's the live ops dashboard showing real events." (Flipping to the live dashboard during the architecture slide = implementation + architecture points simultaneously.)

**[5:45 Close]** Flywheel + endgame: *"Every return RELAY grades makes the next grade smarter and the next price truer. Marketplaces sell items. We sell trust — per item, at the doorstep. Returns that never return."*

## 7.2 Slide order (≤10)
1. Title + tagline 2. The absurd journey (one map, one number) 3. The cost stack of a return 4. Insight: "returns become transfers" 5. **[LIVE DEMO]** 6. Trust system: fingerprint + certificate 7. Target architecture 8. Metrics: $/return saved, km saved, kg landfill diverted, fraud caught 9. Business model + flywheel 10. Roadmap → "the UPI of second-life commerce"

## 7.3 Stagecraft notes
- Physical props are unbeatable: real product + the "fraud" twin + a printed RELAY tamper-bag mock (₹200 at a print shop, looks like a funded company).
- Assign the room: presenter never touches the keyboard; one driver, one phone operator, one on judge eye-contact.
- Pre-stage every screen one click deep. No live typing, no live login, no live WiFi dependency (fallback ladder).
- Emotional pacing: absurdity (laugh) → competence (quiet) → fraud catch (gasp) → moneyshot (memory). Engineer all four; the gasp and the memory are what get scored hours later.

---

# SECTION 8 — UI/UX STRATEGY

**Direction: "Amazon meets Apple Wallet."** Familiar commerce bones (cards, clean lists, trust badges) + one signature premium layer (the certificate and scan experience). Hackathon UIs fail by being uniformly flashy; funded-looking UIs are calm with two or three deliberate showpieces.

- **System:** Tailwind + shadcn/ui, Inter font, an 8-pt grid. Light UI for consumer flow; **dark UI for the ops dashboard** (instant "mission control" credibility and visual separation between the two products you're demoing).
- **Color:** neutral slate base; one trust color (deep green) reserved *exclusively* for verification states; one alert red reserved exclusively for the fraud interrupt. Scarcity of color = meaning of color.
- **Scan experience:** full-bleed camera, thin progress ring, instruction text that *types itself* (streaming = alive), gentle haptic-style pulse on each accepted frame. Rejected frame shakes once. These three micro-behaviors are 80% of perceived intelligence.
- **Certificate:** modeled on a grading slab / boarding pass: heavy letter grade, microtext, QR, subtle guilloché-style background, a slow sheen animation on mint. Make it screenshot-worthy — judges photograph demos, give them the frame.
- **Confidence displays:** thin radial gauges, animate from 0 on reveal, always with the label of *what* the confidence is about. Numbers counting up are cheap dopamine — use for match %, km saved, ₹ saved.
- **Map:** dark map style, pulsing demand pins, a drawn route line with the distance chip. (Leaflet + free dark tiles is enough; Mapbox if time.)
- **Sustainability:** one quiet card — "2.1 kg CO₂e and 3,496 km avoided" — not a green-washed dashboard. Restraint reads senior.
- **Motion rules:** every animation ≤400ms except the three showpieces (fingerprint compare, certificate mint, journey reveal) which earn 1.5–2s. Nothing bounces. Framer Motion, spring presets, done.

---

# SECTION 9 — BUSINESS & SCALING

## 9.1 TAM, framed correctly
Don't pitch "resale market TAM." Pitch the **cost-destruction TAM**: if US returns alone are ~$700B+ of merchandise with $25–40 of reverse-logistics cost each across billions of parcels, the *processing spend* RELAY attacks is in the tens of billions annually — before counting fraud losses ($80–100B+ est.) and recovered resale value. RELAY monetizes pain that already sits on retailer P&Ls, which is the easiest money in B2B.

## 9.2 Revenue model (three stacked layers)
1. **Per-verification fee** — $/return for grade + fraud screen (SaaS wedge; sellable to D2C brands with zero logistics).
2. **Relay take-rate** — 5–10% of direct customer→buyer transfers RELAY routes.
3. **Trust API** — certificates-as-a-service for marketplaces, insurers (returns insurance pricing!), and carriers. This is the rails/UPI layer: neutral infrastructure every player pays to plug into.

## 9.3 Why Amazon specifically wins
Saves $X per return at nine-figure return volumes; weaponizes assets it already owns (delivery photos, Flex network, Renewed demand, Bedrock); converts a cost center into a Prime-grade feature ("instant doorstep refund, verified"); and produces auditable ESG metrics (km eliminated, kg diverted) at a time those numbers are board-level.

## 9.4 The data moat & network effects
Every transaction emits a labeled tuple: photos → defects → grade → price → realized sale → dispute outcome. That is the only dataset in the world that closes the loop from *image to realized second-life price*. It compounds: better grades → fewer disputes → more buyer trust → more demand density → faster matches → more sellers → more data. Demand density is also a classic local-network effect: RELAY gets *better in each city as it grows in that city*, which is exactly the moat shape of Uber/UPI-class platforms.

## 9.5 Expansion ladder
D2C fraud-screen SaaS → retailer doorstep grading → peer relay routing → carrier integration (graded-at-pickup) → cross-marketplace trust certificates → warranty/insurance underwriting data → the reverse-commerce operating system. Each rung is independently revenue-positive; none requires the next to justify itself.

---

# SECTION 10 — COMPETITIVE STRATEGY

## 10.1 The field, and why it loses
Expect: resale marketplaces with AI listings ("OLX + GPT"), returns chatbots, price-prediction dashboards, sustainability scorecards. All share two fatal traits: (a) they accept the warehouse, so they optimize a broken loop instead of deleting it; (b) their AI is decorative (writes descriptions) rather than load-bearing (creates trust). Your positioning sentence: *"Most teams built a better marketplace. We deleted the reason marketplaces are risky."*

## 10.2 Judge Q&A bank (rehearse these out loud)

- **"What if the AI grades wrong?"** → "Grades carry confidence; low confidence routes to human review; the buyer confirms at handoff; disputes feed the model. AI flags, humans accuse — and the dispute loop is the data moat." 
- **"Customers will game it."** → Walk the fraud ladder (serial → embedding → behavioral → courier pickup check → buyer confirmation). "We don't need perfection — we need fraud to be harder than the warehouse makes it today, and today's bar is 'nobody checks until weeks later.'"
- **"What's actually live in the demo?"** → Flip the ops dashboard, show the MOCK badges. Itemize honestly. (This answer wins more points than any feature.)
- **"Why won't Amazon just build this?"** → "They should — that's the point of building it at their hackathon / for their ecosystem. Independently: the trust layer is *more* valuable as neutral rails across retailers, like UPI vs. one bank's wallet."
- **"No nearby buyer — then what?"** → "Disposition engine degrades gracefully: widen radius → list to demand network → liquidation channel → recycle. Relay is the best path, never the only path."
- **"Privacy of doorstep photos?"** → "Customer-initiated capture, item-only framing prompts, retention window tied to dispute period, certificates share grades not raw images."
- **"Isn't the buyer taking the risk the warehouse used to absorb?"** → "The buyer gets *more* information than a warehouse buyer ever did — defect map, confidence, custody log — plus confirmation-gated payment release. Risk isn't transferred; it's shrunk and made legible."

## 10.3 Known weaknesses — own them before judges find them
Doorstep grading is harder for apparel fit/feel (start with electronics & hard goods — say so). Serial-less items need FiberPrint-class techniques (roadmap). Two-sided liquidity is a cold-start problem (wedge is the SaaS fraud screen, which needs zero liquidity). Naming your own weaknesses with mitigations is the single strongest seniority signal in Q&A.

---

# SECTION 11 — CODEBASE & IMPLEMENTATION PLANNING

## 11.1 Repo (monorepo, two apps, one shared contract)

```
relay/
├── apps/
│   ├── web/                      # React + Vite + Tailwind + shadcn
│   │   ├── src/flows/scan/       # camera, checklist, live feedback
│   │   ├── src/flows/certificate/
│   │   ├── src/flows/buyer/
│   │   ├── src/flows/ops/        # dark dashboard
│   │   └── src/lib/api.ts        # typed client (generate from OpenAPI)
│   └── api/                      # FastAPI
│       ├── main.py               # routers only
│       ├── domain/               # session state machine, events
│       ├── services/
│       │   ├── scan.py  fingerprint.py  defects.py  grading.py
│       │   ├── pricing.py  matching.py  fraud.py  carrier_mock.py
│       ├── ai/
│       │   ├── bedrock.py        # client, retries, timeout, prewarm
│       │   ├── prompts/          # versioned .md prompt files
│       │   └── schemas.py        # pydantic mirrors of JSON contracts
│       ├── seed/                 # SKUs, buyers, fingerprints, comps
│       └── fallbacks/            # cached responses per demo SKU
├── packages/contracts/           # OpenAPI + event schemas (source of truth)
└── infra/                        # one deploy script; do not gold-plate
```

## 11.2 API contract (build in this order)

```
POST /sessions                        → {session_id, checklist[]}
POST /sessions/{id}/frames            → {accepted, reason?, next_step}
POST /sessions/{id}/verify            → {identity_confidence, serial_match, verdict}
POST /sessions/{id}/grade             → {grade, defects[], confidence, certificate_id}
GET  /certificates/{id}               → full certificate (public, QR target)
POST /sessions/{id}/disposition       → {path, explanation, price}
GET  /matches/{session_id}            → buyer candidates [{distance_km, fit}]
POST /matches/{id}/reserve            → booking (mock carrier inside)
POST /transfers/{id}/confirm          → releases refund/payment (mock ledger)
GET  /ops/events?session_id=          → custody/event stream for dashboard
```

## 11.3 Data model (DynamoDB single-table or 5 SQLite tables — don't agonize)
`Item{sku, serial, catalog_imgs, base_price, fingerprint{embed_ref, phash, serial}}` · `ReturnSession{state, frames[], defects[], grade, confidence, price, trust_score, events[]}` · `Buyer{geo, wishlist[{sku, max_price, condition_min}]}` · `Transfer{session, buyer, label, status}` · `events` append-only.

## 11.4 Build order (dependency-true)
contracts → bedrock client + defect prompt (against real photos, hour 2) → session API + uploads → fingerprint math → certificate UI → fraud branch → matching/map → dashboard → polish. **The prompt-engineering loop on your real demo photos is the highest-leverage hour in the entire 48 — start it before the frontend exists**, using a notebook.

## 11.5 Stack verdicts
React+Vite+Tailwind+shadcn+Framer Motion; FastAPI+pydantic+boto3; Bedrock Claude Sonnet (vision) + Titan Multimodal Embeddings (fallback: Anthropic API + open CLIP); imagehash + OpenCV; Leaflet dark tiles; deploy = one Docker compose on a single box (ECS/EC2/Fly), frontend on Vercel/CloudFront. CI/CD = a deploy.sh and the discipline to freeze main at H44. Anything fancier is stolen demo-polish time.

---

# SECTION 12 — FINAL WINNING STRATEGY

**The MVP, in one sentence:** a guided AI doorstep inspection that mints a trust certificate, catches a live swap-fraud attempt, matches the item to a buyer 4 km away on a map, and ends on a journey screen proving the item never touched a warehouse — backed by a live ops dashboard and a target architecture you can defend service-by-service.

**The single strongest differentiator:** the **fraud/fingerprint trust layer**. Anyone can demo resale; only you will demo *catching a cheat on stage*. Trust is the unsexy thing every judge knows is the real problem, and you'll be the only team that built it.

**What judges will remember at scoring time:** two images — the red fraud interrupt, and the 4 km vs 3,500 km journey screen — plus one sentence: *"the item never touched a warehouse."* Everything in your build plan exists to make those three memories crisp.

**The biggest risk:** demo fragility (live camera + live inference + live network on stage). It is fully mitigable: fallback ladder, cached SKU results, pre-warmed models, backup video, five rehearsals, WiFi-off test. Treat the demo as a *production system with an SLA* — that mindset, visible in how smoothly it runs, is itself judged.

**How to maximize win probability, ranked by leverage:** (1) rehearse the fraud moment until the timing is theatrical, (2) make the certificate beautiful, (3) nail defect-prompt quality on your exact SKUs early, (4) keep one person on story full-time, (5) freeze at H44, (6) answer "what's mocked?" with radical, dashboard-backed honesty.

**Why this is top-1%:** it inverts the problem (deletes the warehouse instead of decorating it), its AI is load-bearing rather than cosmetic, it demos a *system* (consumer app + buyer app + ops brain + event architecture) rather than a screen, it has a real business wedge, and it owns its weaknesses out loud. That combination — vision + working trust tech + architectural literacy + honest engineering judgment — is precisely what makes a judging panel write the sentence you want in their notes: *"this team is operating at another level."*

---

*Pre-demo checklist: verify the NRF/Optoro statistics and India-specific return figures for your slides; photograph demo SKUs in your actual demo lighting; print the tamper-bag and certificate; charge two phones; export the backup video; sleep.*
