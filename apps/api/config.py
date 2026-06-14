"""Runtime configuration. The AI mode drives the fallback ladder (Section 3.5)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RELAY_", env_file=".env", extra="ignore")

    # ai_mode: "mock" (cached/stub, offline-safe) | "gemini" | "bedrock" | "anthropic"
    #   | "aws" (Gemini vision + Rekognition serial/labels + Bedrock Haiku disposition)
    ai_mode: str = "mock"

    aws_region: str = "us-east-1"
    bedrock_vision_model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    bedrock_embed_model: str = "amazon.titan-embed-image-v1"
    # Cheap text-only model for the disposition explanation (us. inference profile —
    # newer Claude models reject the raw model id for on-demand invocation).
    bedrock_disposition_model: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Gemini (free tier) — the zero-cost hackathon vision provider.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Use the local (free) CLIP-style image embedding for fingerprints when real
    # scan/catalog images are available. Falls back to seeded vectors otherwise.
    use_local_embeddings: bool = True

    ai_timeout_s: float = 6.0

    # Fingerprint thresholds (Section 4.1)
    fp_pass_threshold: float = 0.85
    fp_review_threshold: float = 0.60

    # Trust threshold (Section 4 / step 7)
    trust_threshold: float = 0.70


settings = Settings()
