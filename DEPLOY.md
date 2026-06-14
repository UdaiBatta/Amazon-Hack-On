# Deploying RELAY AI

Two pieces: a static **frontend** and a long-running **backend** (FastAPI with an
in-memory store, event bus, and SSE stream, so it needs a persistent container, not
serverless functions).

> Local dev is unaffected: with `VITE_API_BASE` unset the frontend uses the Vite
> `/api` proxy as before.

---

## Recommended (free, fast): Render backend + Vercel frontend

### 1. Backend → Render
1. Push the repo to GitHub (already done).
2. Render dashboard → New → **Web Service** → connect the repo.
3. Settings:
   - **Root Directory:** `apps/api`
   - **Runtime:** Docker (a `Dockerfile` is provided), or Python with
     start command `uvicorn main:app --host 0.0.0.0 --port $PORT`.
   - **Environment variables:**
     - `RELAY_AI_MODE` = `gemini` (free) or `mock` (offline) or `aws`
     - `RELAY_GEMINI_API_KEY` = your AI Studio key
     - `RELAY_GEMINI_MODEL` = `gemini-2.5-flash-lite`
4. Deploy. Note the URL, e.g. `https://relay-api.onrender.com`.
   - Free tier sleeps after ~15 min idle; open the URL once to warm it before a demo.

### 2. Frontend → Vercel
1. Vercel → New Project → import the repo.
2. Settings:
   - **Root Directory:** `apps/web`
   - **Framework:** Vite (auto). Build `npm run build`, output `dist`.
   - **Environment variable:** `VITE_API_BASE` = your Render backend URL
     (e.g. `https://relay-api.onrender.com`).
3. Deploy. This URL is your "Live App" link for the PRD.

CORS is already open on the backend, and SSE works over the absolute URL.

---

## Amazon-native option (for the "runs on AWS" story + live `aws` mode)

Run the backend container on **AWS App Runner** or a small **EC2 t3.micro**, and
attach an **IAM role** with `rekognition:DetectText`, `rekognition:DetectLabels`,
and `bedrock:InvokeModel`. The instance role supplies AWS creds automatically, so
`RELAY_AI_MODE=aws` works with no keys to manage. Frontend can stay on Vercel, or
go to **S3 + CloudFront** to match the target architecture.

- App Runner: point it at the GitHub repo / `apps/api/Dockerfile`, set the same env
  vars (minus AWS keys, the role handles those), attach the role.
- Enable Bedrock model access for Claude Haiku in the AWS console first, or `aws`
  mode falls back to the deterministic disposition text (still fine).

---

## Notes
- **State is in-memory and single-instance** by design (demo). It resets on restart
  and does not scale horizontally. Production path = DynamoDB + S3 + OpenSearch
  (see the masterplan target architecture).
- For a guaranteed Grade B stage run, deploy with `RELAY_AI_MODE=mock` (serves the
  cached real-Gemini output). Use `gemini`/`aws` to show a genuinely-live call.
- Quick local container test:
  `docker build -t relay-api apps/api && docker run -p 8000:8000 relay-api`
