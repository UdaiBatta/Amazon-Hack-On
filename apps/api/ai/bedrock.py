"""The AI client + the fallback ladder (Section 3.5).

  1. Live call (Bedrock Claude vision / Titan embeds) with a hard timeout, OR
     Anthropic API direct (same prompts) —
  2. Cached response for the demo SKU (identical schema) —
  3. Local rule-based stub (serial regex + canned defects) —
  4. "Inspector review queued" graceful state.

The demo NEVER blocks on a network call. `prewarm()` fires a dummy inference on
startup and every 60s to dodge Bedrock cold-start death.
"""
from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Optional

from config import settings

_PROMPT_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPT_DIR / name).read_text()


def _extract_json(text: str) -> dict:
    """Tolerant JSON extraction with retry-with-repair semantics."""
    text = text.strip()
    # strip markdown fences if present
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


class AIClient:
    """Provider-agnostic AI client. `mode` ∈ {mock, gemini, bedrock, anthropic}.

    Default hackathon provider is `gemini` (free tier). Same prompts/schema work
    across providers — perception is a stateless model call, so production swaps
    the provider without touching the architecture.
    """

    def __init__(self) -> None:
        self.mode = settings.ai_mode
        self._bedrock = None
        self._defect_prompt = _load_prompt("defect_extraction.md")
        self._frame_prompt = _load_prompt("frame_validation.md")

    # -- lazy clients --------------------------------------------------- #
    def _bedrock_client(self):
        if self._bedrock is None:
            import boto3

            self._bedrock = boto3.client(
                "bedrock-runtime", region_name=settings.aws_region
            )
        return self._bedrock

    async def prewarm(self) -> None:
        """Keep models warm. Only meaningful for Bedrock (provisioned cold-starts).

        Skipped for Gemini/Anthropic (hosted, no cold-start) — and crucially this
        avoids burning the Gemini free-tier daily quota with idle pings.
        """
        if self.mode != "bedrock":
            return
        try:
            await asyncio.wait_for(
                self._raw_text("ping", images=[]), timeout=settings.ai_timeout_s
            )
        except Exception:
            pass

    # -- low level ------------------------------------------------------ #
    async def _raw_text(self, prompt: str, images: list[bytes]) -> str:
        """One vision/text call. Runs blocking SDKs in a thread."""
        if self.mode == "gemini":
            return await self._gemini_invoke(prompt, images)
        if self.mode == "bedrock":
            return await asyncio.to_thread(self._bedrock_invoke, prompt, images)
        if self.mode == "anthropic":
            return await self._anthropic_invoke(prompt, images)
        raise RuntimeError("no live mode")

    async def _gemini_invoke(self, prompt: str, images: list[bytes]) -> str:
        """Google Gemini (free tier). Forces JSON output via responseMimeType."""
        import base64

        import httpx

        parts: list[dict] = [{"text": prompt}]
        for img in images:
            parts.append(
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img).decode(),
                    }
                }
            )
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent"
        )
        async with httpx.AsyncClient(timeout=settings.ai_timeout_s) as client:
            resp = await client.post(
                url,
                params={"key": settings.gemini_api_key},
                json={
                    "contents": [{"parts": parts}],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.2,
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def _bedrock_invoke(self, prompt: str, images: list[bytes]) -> str:
        import base64

        content: list[dict] = [{"type": "text", "text": prompt}]
        for img in images:
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64.b64encode(img).decode(),
                    },
                }
            )
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": content}],
        }
        resp = self._bedrock_client().invoke_model(
            modelId=settings.bedrock_vision_model, body=json.dumps(body)
        )
        payload = json.loads(resp["body"].read())
        return payload["content"][0]["text"]

    async def _anthropic_invoke(self, prompt: str, images: list[bytes]) -> str:
        import base64

        import httpx

        content: list[dict] = [{"type": "text", "text": prompt}]
        for img in images:
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64.b64encode(img).decode(),
                    },
                }
            )
        async with httpx.AsyncClient(timeout=settings.ai_timeout_s) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": content}],
                },
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]

    # -- high level: defect extraction (ladder applied) ----------------- #
    async def extract_defects(
        self,
        product_name: str,
        category: str,
        images: list[bytes],
        cached: dict,
        stub: dict,
    ) -> tuple[dict, str]:
        """Returns (result_dict, source) where source ∈ live|cache|stub."""
        prompt = self._defect_prompt.format(
            product_name=product_name, category=category, n_images=len(images)
        )
        # rung 1: live
        if self.mode != "mock" and images:
            try:
                text = await asyncio.wait_for(
                    self._raw_text(prompt, images), timeout=settings.ai_timeout_s
                )
                return _extract_json(text), "live"
            except Exception:
                pass
        # rung 2: cached happy-path for demo SKU
        if cached:
            return cached, "cache"
        # rung 3: rule stub
        return stub, "stub"

    async def validate_frame(
        self,
        product_name: str,
        requested_view: str,
        image: Optional[bytes],
    ) -> tuple[dict, str]:
        prompt = self._frame_prompt.format(
            product_name=product_name, requested_view=requested_view
        )
        if self.mode != "mock" and image:
            try:
                text = await asyncio.wait_for(
                    self._raw_text(prompt, [image]), timeout=settings.ai_timeout_s
                )
                return _extract_json(text), "live"
            except Exception:
                pass
        # offline: accept (the demo drives correctness via the cached path)
        return {
            "is_requested_view": True,
            "detected_view": requested_view,
            "redirect_message": None,
            "confidence": 0.92,
        }, "stub"


ai = AIClient()
