# RELAY AI — Project Handout

> **Living collaboration doc.** Read this BEFORE every session. Update the
> **Session Log** and **Status** sections AFTER every session. This is the single
> source of truth for *where the project is*; `RELAY_AI_Masterplan.md` is the
> source of truth for *what we're building and why*.

---

## 0. How to use this doc (the ritual)

> **⚠️ ALWAYS read the masterplan first.** Before doing anything, open and re-read
> `/Users/samarthchatli/amazon hack/RELAY_AI_Masterplan.md` every session. It is the
> source of truth for *what we're building and why* (strategy, UX direction, AI
> workflows, demo script, MVP priorities). This HANDOUT is the source of truth for
> *where the project is*. If reality drifts from the masterplan, or we make a
> decision that changes the plan, **update the masterplan too** and note it in the
> Session Log (§10). The two docs must never contradict each other.

**Before a session:**
1. **Read `RELAY_AI_Masterplan.md` end-to-end (or the relevant sections).**
2. Read §1 (one-liner) + §2 (status) + §7 (what's next) of this handout.
3. Skim the most recent entries in §10 (Session Log).
4. Pick a task from §8 (Roadmap) or continue an in-progress item.

**After a session:**
1. Update §2 status checkboxes.
2. Add a §10 Session Log entry (date, who/what, decisions, what broke).
3. Move completed items out of §7/§8 and tick them in §2.
4. Add any new TODOs or gotchas you discovered.
5. **If anything changed the strategy/scope/architecture, update
   `RELAY_AI_Masterplan.md`** and record the edit in the Session Log.

Keep it honest. "Half-working" is more useful to a teammate than "done."

---

## 1. What RELAY is (one-liner)

A trust + routing layer for reverse commerce. Doorstep AI inspection mints a trust
certificate, catches swap-fraud live, and routes a returned item directly to a
nearby buyer — **so the item never touches a warehouse.**

Demo spine: Orders → Guided Scan → Fingerprint Verify → Grade Certificate →
Disposition → Buyer Match (map) → Journey moneyshot. Plus a dark Ops dashboard.

Philosophy: **AI perceives, rules decide.**

---

## 2. Current status (last updated: 2026-06-13, Session 5)

### Done ✅
- [x] Monorepo scaffold (`apps/api`, `apps/web`)
- [x] FastAPI monolith with target-architecture module boundaries
- [x] Structured-output contract (`ai/schemas.py`) — defect extraction + frame validation
- [x] **Provider-agnostic AI client** — `gemini` (free tier) / `bedrock` / `anthropic` / `mock`
- [x] AI client with **4-rung fallback ladder** (live → cached → stub → review), prewarm loop
- [x] **Gemini Flash adapter** (free tier) for defects + serial OCR + frame validation, JSON-forced
- [x] **Local zero-cost image embeddings** (`services/embeddings.py`, Pillow+numpy, no torch)
- [x] Fingerprint service — real cosine + pHash + serial; uses local embeddings when photos exist
- [x] Grading rubric (deterministic, config-driven) + confidence
- [x] Pricing heuristic v1 (grade × decay × demand) + rationale
- [x] Fraud/trust scoring + behavioral flags
- [x] Disposition engine (rules + explanation), graceful degradation
- [x] Buyer matching (haversine, proximity-dominant ranking) + demand pins
- [x] Mock carrier behind real interface; mock transfer/refund confirm
- [x] Event bus + append-only custody ledger + SSE live stream
- [x] Seed data: 3 SKUs, 12 buyers, demo order, fraud swap unit
- [x] Frontend: all 7 consumer flow screens + Ops dashboard + Buyer view
- [x] Real camera capture + on-device quality gate (Laplacian/brightness/fill)
- [x] Buyer-side phone view (`/buyer`) — live demand feed, reserve, confirm; idempotent reserve
- [x] Real scan frames stored + fed to live vision model at grade time
- [x] **Amazon storefront reskin** across seller app, buyer feed, and ops dashboard
      (squid/navy/yellow/orange palette, Amazon nav, yellow CTAs, "Your Orders" page)
- [x] End-to-end verified (TestClient + live proxy): happy + fraud + buyer paths
- [x] `smoke_test.py` passes; `npm run build` clean; zero diagnostics

### In progress 🔧
- [ ] (none currently — pick from Roadmap §8)

### Not started ⬜
- [ ] Add catalog reference photos to `seed/catalog_images/` to activate real fingerprint match
- [ ] Shoot the 3 SKUs (+ swap unit) and run a full live pass to tune prompts
- [ ] Per-frame Gemini validation driving real redirects (kept fast/scripted for now)
- [ ] Slides + rehearsal + backup video *(presentation work, not code)*

> ✅ **Live Gemini configured + Amazon UI shipped.** Key is in `apps/api/.env`
> (gitignored). **Current mode is `mock`** for a reliable Grade B demo (serves the
> cached real-Gemini output on the actual JBL, in `fallbacks/cached.py`). Flip
> `RELAY_AI_MODE=gemini` and point the camera at the real JBL only to show a
> genuinely-live call. Live model: **`gemini-2.5-flash-lite`** (2.5-flash = 20/day,
> 2.0-flash = 0/day free quota).

---

## 3. How to run

### Backend
```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- Default `RELAY_AI_MODE=mock` → fully offline (cached + stub). Demo-safe, $0.
- **Live AI ($0):** copy `.env.example` → `.env`, set `RELAY_AI_MODE=gemini` +
  `RELAY_GEMINI_API_KEY` (free key: https://aistudio.google.com/apikey, no billing).
  Optional paid: `anthropic` + `RELAY_ANTHROPIC_API_KEY`, or `bedrock` + AWS creds.
- **Real fingerprint ($0):** drop a photo per SKU in `seed/catalog_images/{sku}.jpg`.
- **Stage / WiFi-off run:** set `RELAY_AI_MODE=mock` → zero network calls, serves the
  cached real-Gemini result; maximally reliable. Flip to `gemini` only to show a
  live call. The web app has no CDN deps (fonts + Leaflet CSS vendored); the map
  degrades to a stylized dark grid if tile servers are unreachable.
- Smoke test: `.venv/bin/python smoke_test.py`

### Frontend
```bash
cd apps/web
npm install
npm run dev      # http://localhost:5173  (proxies /api → :8000)
```
- Consumer app: `/`  ·  Ops dashboard: `/ops`
- **Fraud demo:** toggle "Scan the swap unit" checkbox at the bottom of the phone.

### Ports
- API: `8000` · Web: `5173` · Web proxies `/api/*` → API (strips `/api`).

---

## 4. Architecture map (file → responsibility)

```
apps/api/
  main.py                 routers only + lifespan prewarm loop
  config.py               settings (AI mode, thresholds)
  ai/
    schemas.py            DefectExtraction / FrameValidation contracts (build-first)
    bedrock.py            AIClient: fallback ladder, bedrock+anthropic adapters, prewarm
    prompts/*.md          versioned prompts (defect_extraction, frame_validation)
  domain/
    models.py             Item, ReturnSession, Buyer, Transfer, Event, enums
    store.py              in-memory repo (swap-to-DynamoDB seam)
    events.py             EventBus (EventBridge analogue) + canonical event types
  services/
    fingerprint.py        cosine + pHash + serial → identity composite
    defects.py            orchestrates AI extraction + chooses cached vs fraud unit
    grading.py            rubric (SEVERITY_PENALTY, BANDS) → grade  [RULES DECIDE]
    pricing.py            heuristic v1
    fraud.py              trust score + behavioral flags
    matching.py           haversine, ranking, demand_pins
    disposition.py        routing rules + explanation
    carrier_mock.py       MockCarrier behind CarrierService Protocol
  routers/                sessions, matches, transfers, certificates, ops, catalog, buyer
  seed/                   catalog.py (SKUs+fingerprints+DEMO_ORDER), buyers.py
  fallbacks/              cached.py (per-SKU + fraud unit), stub.py

apps/web/src/
  App.tsx                 consumer flow state machine + stage controls (fraud toggle)
  lib/api.ts              typed client
  lib/quality.ts          on-device capture quality gate (Laplacian/brightness/fill)
  components/ui.tsx       CountUp, RadialGauge, SeverityChip, StreamingStatus, Button
  flows/orders|scan|verify|certificate|match|journey/   consumer screens
  flows/scan/Scan.tsx     real camera (getUserMedia) + quality gate + staged redirect
  flows/buyer/BuyerView   buyer phone (route /buyer): demand feed → reserve → confirm
  flows/ops/OpsDashboard  dark mission-control (SSE feed + service registry + metrics)
```

---

## 5. API reference (current)

| Method | Path | Purpose |
|---|---|---|
| GET | `/catalog/orders` | seller's order list (return entry point) |
| GET | `/catalog/items` | SKUs + capture checklists |
| POST | `/sessions` | create ReturnSession → checklist |
| POST | `/sessions/{id}/frames` | submit guided-scan frame |
| POST | `/sessions/{id}/verify` | fingerprint identity + trust/fraud screen |
| POST | `/sessions/{id}/grade` | defects + grade + price + certificate id |
| POST | `/sessions/{id}/disposition` | routing decision |
| GET | `/sessions/{id}` | full session state |
| GET | `/matches/{id}` | ranked buyers + demand pins + seller pin |
| POST | `/matches/{id}/reserve` | reserve → book mock carrier (idempotent) |
| GET | `/buyer/{buyer_id}/feed` | buyer's demand feed (matched/reserved/confirmed cards) |
| POST | `/transfers/{id}/confirm` | release refund/payment → journey payload |
| GET | `/certificates/{cert_id}` | public certificate (QR target) |
| GET | `/ops/events?session_id=` | custody/event log |
| GET | `/ops/stream` | SSE live event feed |
| GET | `/ops/services` | REAL/MOCK/SEEDED/ROADMAP registry |
| GET | `/ops/metrics` | headline demo metrics |

`verify` and `grade` take `fraud_mode` (bool) — the stage switch for the swap demo.

---

## 6. Demo facts (the numbers that must stay consistent)

- **Demo SKU:** `SKU-HP-01` JBL Tune 770NC (Black), base ₹5,599, serial `SN-77109`.
- **Happy result:** Grade **B**, score **73**, resale **₹4,140**, refund ~₹3,890.
  Defects are **real Gemini output on the actual JBL** (cached for reliability).
- **Hero buyer:** **Rohan @ ~4.27 km** (must remain top match; 7 HP demand pins).
- **Fraud unit serial:** `SN-88412` → mismatch → trust fails → review.
- **Journey:** RELAY ~4.3 km / 0 warehouses / 1 hop  vs  old world 3,500 km / 2 / 19 days.
- **Seller location:** Patiala (30.3398, 76.3869) — matches the masterplan story.

> ⚠️ If you change `base_price`, cached defects, or buyer `max_price`/coords,
> re-run `smoke_test.py` — the Grade-B + DIRECT_RELAY + Rohan-top invariants are
> tuned and brittle. See §8 "Pricing/matching are coupled to seed data."

---

## 7. What's next (immediate, pick one)

1. **Validate live AI on real photos** (highest leverage). Set `anthropic` mode,
   shoot the 3 SKUs + swap unit in demo lighting, iterate `prompts/defect_extraction.md`
   until grades/serials are crisp. Keep cached results as the fallback safety net.
2. **Real camera capture** in `flows/scan/Scan.tsx` — replace the staged viewport
   with `getUserMedia`, push frames to `/frames`, keep client-side blur/brightness gate.
3. **Buyer-side view** — a second phone screen for Rohan (push card → reserve).
4. **Slides + rehearsal + backup video** (Section 7 of masterplan).

---

## 8. Roadmap — streamlining the whole process

### Near-term (hackathon polish)
- [ ] Live AI mode tested + prompt-tuned on real SKU photos
- [x] Client-side capture quality gate (Laplacian blur, brightness, fill %)
- [ ] Per-frame Claude validation actually driving real redirects (currently scripted)
- [x] Buyer-side phone view + cross-device "reserve" sync (idempotent)
- [ ] Certificate as a shareable public page (QR opens `/certificates/{id}`)
- [ ] Latency theater tuned to real call times; "optimistic resolve" at 4s
- [ ] Backup screen-capture video of the perfect run
- [ ] WiFi-off rehearsal pass (prove the fallback ladder on stage)

### Mid-term (make it a product, not a demo)
- [ ] Swap in-memory store → DynamoDB (single-table `PK=SESSION#id`) behind `domain/store.py`
- [ ] Real media pipeline: presigned S3 PUT → `raw/` → thumbnails → certificate refs
- [ ] Titan Multimodal / CLIP embeddings for real fingerprints (replace seeded vectors)
- [ ] Real serial OCR (Claude vision or Textract) instead of seeded serial
- [ ] Pricing v2: gradient-boosted model on realized resale outcomes (the data flywheel)
- [ ] OpenSearch for geo + k-NN buyer matching (replace haversine/numpy)
- [ ] Auth (Cognito) + per-role sessions (currently hardcoded single user)
- [ ] Carrier adapter → real Shiprocket/Delhivery/UPS booking
- [ ] Payments/refund ledger → real settlement rail
- [ ] Event bus → EventBridge + SQS + DLQs; Step Functions for the session workflow
- [ ] Observability: CloudWatch/X-Ray, structured logs, idempotency keys

### Long-term (the rails business)
- [ ] FiberPrint micro-texture authentication (currently ROADMAP-only story)
- [ ] Trust API / certificates-as-a-service for marketplaces + insurers
- [ ] Dispute loop → labeled dataset (photos → defects → grade → price → outcome)
- [ ] Multi-city demand-density network effects; cold-start via D2C fraud-screen SaaS
- [ ] ESG reporting surface (km eliminated, kg diverted, fraud caught)

### Tech-debt / cleanup
- [ ] `Scan.tsx` redirect is hardcoded (`REDIRECT_AT="serial"`) — move to backend signal
- [ ] Frontend bundle >500 kB — code-split Leaflet/map route if it matters
- [ ] No automated frontend tests; only backend `smoke_test.py`
- [ ] `allow_origins=["*"]` CORS — tighten before any real deploy
- [ ] Pricing & matching invariants coupled to seed data (see §6 warning)

---

## 9. Real vs mocked (keep this answer ready for judges)

| Capability | Status | Where |
|---|---|---|
| Defect detection | **REAL** (Gemini Flash free tier, cached fallback) | `services/defects.py`, `ai/` |
| Serial OCR | **REAL** (Gemini vision, inside defect call) | `ai/bedrock.py` |
| Fingerprint identity | **REAL** (local embedding + pHash + serial) | `services/fingerprint.py`, `services/embeddings.py` |
| Grading | **REAL** (deterministic rubric) | `services/grading.py` |
| Trust/fraud | **REAL** (composite + flags) | `services/fraud.py` |
| Disposition | **REAL** (rules + explanation) | `services/disposition.py` |
| Matching | **REAL logic / SEEDED data** | `services/matching.py`, `seed/` |
| Pricing | **REAL (v1 heuristic)** | `services/pricing.py` |
| Carrier booking | **MOCK** | `services/carrier_mock.py` |
| Payments/refund | **MOCK** | `routers/transfers.py` |
| Delivery-time fingerprint | **SEEDED** | `seed/catalog.py` |
| FiberPrint | **ROADMAP** | story only |

The Ops dashboard (`/ops`) renders these badges live. Flip to it when asked
"what's real?"

---

## 10. Session log (newest first)

### 2026-06-13 — Session 5 (Amazon UI reskin + demo mode)
- **Why:** make the whole app look like a real Amazon storefront (judge perception).
- **Built / changed:**
  - Amazon palette in `tailwind.config.js` (`amzn.*`: squid #131921, navy #232F3E,
    yellow #FFD814, orange #FF9900, search #FEBD69, bg #EAEDED, price #B12704,
    link #007185). Font stack set to Amazon Ember with Arial fallback. `ink` unified
    to squid. Page bg gray.
  - New `components/AmazonNav.tsx`: squid top bar with `relay.ai` + smile logo,
    Deliver-to, search bar + yellow search button, Account, and bordered Buyer/Ops
    buttons; navy secondary strip. Hardcoded hex so it never depends on config state.
  - `PrimaryButton` is now the Amazon yellow pill; added `SecondaryButton` (squid).
  - `Orders` rebuilt as a real Amazon "Your Orders" page (header band, teal titles,
    Buy-it-again / Return-or-replace pills).
  - Yellow forward CTAs across Verify, Certificate, Match (reserve), Journey; trust
    green kept for verification, alert red for fraud only. Cleaned UI em-dashes and
    the journey route diagrams (now arrows).
  - Buyer view: Amazon squid header + navy strip; Reserve is the yellow buy button.
  - Ops dashboard: Amazon pass — squid bg, top bar with logo + orange accent line,
    orange highlights on impact metrics, Store/Buyer nav links; kept dark
    mission-control feel. Fixed em-dash in the heading.
- **Two bugs fixed mid-session:**
  - Header looked washed out (white text on white): the live dev server was on a
    stale Tailwind config. Fix = restart dev server + hardcode nav hex.
  - Flow ended on RECYCLE / Grade D: that was live Gemini grading whatever the
    webcam saw, not the JBL. Fix = set `RELAY_AI_MODE=mock` (serves cached real
    Gemini Grade B). **Current .env is `mock`.** Flip to `gemini` + point camera at
    the real JBL only for a live-proof moment.
- **Verified:** `npm run build` clean, zero diagnostics on all reskinned files.
- **Gotcha:** after editing `tailwind.config.js`, restart the Vite dev server or new
  color tokens won't render in dev (they build fine in prod).
- **Next:** screenshots for the PRD (grade certificate, fraud interrupt, buyer map),
  architecture + workflow diagrams, run-of-show script, backup video.

### 2026-06-13 — Session 4 (WiFi-off hardening + certificate polish)
- **WiFi-off pass:** vendored Inter font (`@fontsource/inter`) and Leaflet CSS into
  the bundle (removed Google Fonts + unpkg CDN `<link>`s from index.html). Map tile
  layer now degrades to a stylized dark grid (CSS on `.leaflet-container`) when tile
  servers are unreachable — pins/route are vector overlays, no network. Verified:
  full demo runs in `mock` mode with zero network (happy + fraud + buyer).
  Recommended stage config: `RELAY_AI_MODE=mock` (serves cached real-Gemini result),
  flip to `gemini` only for a live-proof call.
- **Certificate polish:** replaced the fake QR grid with a **real scannable QR**
  (`qrcode.react`, encodes `relay.trust/verify/{cert_id}`), added a microtext strip
  and an "Issued … / Scan to verify" boarding-pass footer. Build clean, 0 diagnostics.
- **Next (Session 5 candidates):** record backup video of the perfect run; rehearse
  fraud-moment timing; optional buyer-side certificate view via QR.

### 2026-06-13 — Session 3 (zero-cost AI: Gemini + local embeddings)
- **Why:** avoid recurring Claude API cost; want free + scalable + judge-impressive.
- **Decision:** vision provider = **Google Gemini 2.0 Flash free tier** ($0, no
  billing, frontier vision, no local compute — ideal for the 8 GB M1). Fingerprint
  embeddings = **local on-device perceptual embedding** (Pillow+numpy, no torch,
  no download). Bedrock/Claude/Titan remain the production/target picks; client is
  provider-agnostic. Recorded in masterplan §3.1.
- **Built:**
  - `gemini` mode in `ai/bedrock.py` (`_gemini_invoke`, JSON-forced via
    `responseMimeType`); config keys `RELAY_GEMINI_API_KEY` / `RELAY_GEMINI_MODEL`.
  - `services/embeddings.py` — colour-histogram + gradient signature, L2-normalised;
    `reference_embedding(sku)` reads `seed/catalog_images/{sku}.jpg` if present.
  - Wired: frames endpoint stores raw bytes + computes scan embedding; grade feeds
    real frames to the live model; verify uses real embeddings when both scan +
    catalog images exist (else seeded). Ops `/services` shows the active provider.
  - `.env.example` rewritten around Gemini; `seed/catalog_images/README.md` added.
- **Verified:** embeddings give real signal (same-unit cosine 0.89 vs swap 0.0);
  `gemini` mode with no key falls back gracefully (defects→cache, frames→stub);
  `smoke_test.py` passes; live `/ops/services` reflects mode.
- **Cost:** $0. Gemini free tier ~1,500 calls/day; everything else local/rules.
- **Gotchas:**
  - Real fingerprint match needs BOTH a catalog photo (`seed/catalog_images/`) AND a
    live scan frame; otherwise both sides use seeded vectors (demo-safe default).
  - Gemini free tier rate limit ~15 req/min — fine for demo, not load tests.
  - `frame_bytes` is kept in-memory per session; restart clears it.
- **Next:** get the free Gemini key + shoot the 3 SKUs (+ swap unit) to go fully
  live; then wire per-frame validation to replace the scripted redirect.

#### Session 3 addendum (live key configured)
- Gemini key added to `apps/api/.env` (gitignored), mode=`gemini`.
- **Free-tier quota is tiny on this (new) project:** `gemini-2.0-flash` = **0/day**,
  `gemini-2.5-flash` = **20/day**. **`gemini-2.5-flash-lite` works** (own daily
  bucket, faster/no "thinking") → **that's the model in `.env`**.
- **Prewarm disabled for Gemini** (`prewarm()` now Bedrock-only) — it was about to
  drain the daily quota with 60s idle pings.
- **Demo strategy = masterplan §3.4 "pre-run + cache":** ran ONE real Gemini call on
  the actual JBL front photo, captured the real defect JSON (wear on both earcup
  edges + headband + a scuff), and **baked it into `fallbacks/cached.py` for
  SKU-HP-01**. The demo serves this real-AI result reliably; honest line: *"real
  Gemini output on this exact unit, cached so a live rate limit can't break the
  stage run."* Still Grade B (score 73), resale ₹4,140 — all invariants hold.
- Reference photo saved at `seed/catalog_images/SKU-HP-01.jpeg` (loader now accepts
  jpg/jpeg/png/webp).
- **Gotcha:** don't rely on live Gemini during the stage demo — 20/day is too
  fragile. Keep mode=gemini for "it's really running" proof on a fresh call or two,
  but the cached path carries the actual run. Quota resets daily (Pacific midnight).
- **Next:** optional — take a 2nd front photo to test real live fingerprint match;
  decide Option A (simulated swap) vs B (real-mismatch reference) for fraud.

### 2026-06-13 — Session 2 (camera + buyer view)
- **Built:**
  - Real camera capture in `flows/scan/Scan.tsx` via `getUserMedia` + new
    `lib/quality.ts` on-device gate: Laplacian-variance blur, mean-luma brightness,
    center-contrast fill. Live metric chips + reticle turns green when ready;
    rejected frames shake. Captures real JPEG → `/frames` (multipart). Graceful
    fallback to the simulated emoji viewport if no camera/permission.
  - Buyer-side phone at route `/buyer` (`flows/buyer/BuyerView.tsx`): polls
    `/buyer/{id}/feed` every 2s, shows the push/match card, Reserve, then Confirm
    receipt → mini journey summary. Header links added between seller/buyer/ops.
  - Backend: new `routers/buyer.py` feed endpoint; `reserve` made **idempotent**
    (seller + buyer tabs share one booking); `api.ts` gains `submitFrame(image?)`
    and `buyerFeed`.
- **Verified:** `smoke_test.py` extended (buyer feed + idempotent reserve +
  confirm) — passes. `npm run build` clean. Live proxy check: Rohan's feed returns
  Grade B / ₹4,140 / 4.27 km card.
- **Decisions:**
  - Camera is best-effort with graceful fallback (UI-level fallback ladder) so the
    demo never breaks if the laptop cam is awkward. Quality thresholds are
    conservative (BLUR_MIN=8) to keep the flow moving on webcams — retune for the
    actual demo device/lighting.
  - Single shared in-memory store makes two-tab (seller+buyer) demo work with no
    websockets; buyer view just polls.
  - Masterplan unchanged — this session executed already-planned scope (Section 2
    Steps 2/9/11, Section 3.1). No strategy drift.
- **Gotchas:**
  - Quality thresholds in `lib/quality.ts` are device/lighting sensitive — test on
    the real demo machine and adjust `BLUR_MIN`/`BRIGHT_*`/`FILL_MIN`.
  - Buyer feed returns ALL matching sessions for Rohan (newest first); the view
    uses `cards[0]`. Restart backend to clear accumulated demo sessions.
  - getUserMedia needs https or localhost — fine for local demo, plan for deploy.
- **Next:** validate live AI on real SKU photos (needs key + photos); wire per-frame
  Claude validation to replace the scripted redirect; slides + backup video.

### 2026-06-13 — Session 1 (initial build)
- **Built:** entire MVP spine end-to-end. Backend (FastAPI monolith, all services,
  seed data, fallback ladder, event bus/SSE) + frontend (7 consumer screens + ops
  dashboard) + animations.
- **Verified:** `smoke_test.py` passes; happy path (Grade B, ₹4,140, DIRECT_RELAY,
  Rohan @ 4.27 km, 3,497 km avoided) and fraud path (SN-88412 mismatch → review).
  Live Vite proxy + SSE replay (17 events) confirmed. `npm run build` clean, zero
  diagnostics.
- **Decisions:**
  - In-memory store (not DynamoDB) for demo stability; behind a repo seam.
  - Default `mock` AI mode — runs fully offline; live modes wired but untested.
  - Tuned seed data so Rohan is the hero match at ~4.27 km (proximity-dominant
    ranking weight 0.85/0.15). Lowered headphone base to ₹5,599 to fit buyer budgets.
  - Scan AI redirect is scripted client-side (one redirect at the serial step).
- **Gotchas / brittle:** pricing + matching invariants are coupled to seed data —
  re-run smoke test after any seed change. Bundle >500 kB (fine for demo).
- **Next:** validate live AI on real SKU photos; real camera capture; buyer view;
  slides + backup video.

<!-- TEMPLATE for new entries:
### YYYY-MM-DD — Session N (title)
- **Built:**
- **Verified:**
- **Decisions:**
- **Gotchas:**
- **Next:**
-->
