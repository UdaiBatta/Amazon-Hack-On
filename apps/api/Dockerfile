FROM python:3.13-slim

WORKDIR /app

# deps first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Offline-safe default; override in the host's env (RELAY_AI_MODE, RELAY_GEMINI_API_KEY, ...)
ENV RELAY_AI_MODE=mock

# Hosts (Render/Railway/App Runner) inject $PORT; default 8000 locally.
EXPOSE 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
