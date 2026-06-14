"""Defect extraction orchestration: applies the fallback ladder and picks the right
cached response for the demo (happy path vs. planted fraud unit).

The `fraud_mode` flag is how the demo driver triggers the swap unit on stage —
in production this is just whatever the camera sees.
"""
from __future__ import annotations

from ai.bedrock import ai
from ai.schemas import DefectExtraction
from domain.models import Item
from fallbacks.cached import CACHED_DEFECTS, CACHED_FRAUD_UNIT
from fallbacks.stub import stub_extraction

_CATEGORY = {
    "SKU-HP-01": "headphones",
    "SKU-SH-01": "footwear",
    "SKU-AP-01": "small appliance",
}


async def extract(
    item: Item, images: list[bytes], fraud_mode: bool = False
) -> tuple[DefectExtraction, str]:
    cached = CACHED_FRAUD_UNIT if fraud_mode else CACHED_DEFECTS.get(item.sku, {})
    stub = stub_extraction(item)
    raw, source = await ai.extract_defects(
        product_name=item.name,
        category=_CATEGORY.get(item.sku, "consumer good"),
        images=images,
        cached=cached,
        stub=stub,
    )
    return DefectExtraction.model_validate(raw), source
