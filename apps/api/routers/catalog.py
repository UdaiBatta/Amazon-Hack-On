"""Catalog + demo order surface for the consumer app's order list."""
from __future__ import annotations

from fastapi import APIRouter

from domain.store import store
from seed.catalog import DEMO_ORDER

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/items")
async def items():
    return {
        "items": [
            {
                "sku": item.sku,
                "name": item.name,
                "base_price": item.base_price,
                "checklist": [s.model_dump() for s in item.capture_checklist],
            }
            for item in store.items.values()
        ]
    }


@router.get("/orders")
async def orders():
    """The seller's mock Amazon-style order list (the return entry point)."""
    item = store.get_item(DEMO_ORDER["sku"])
    return {
        "orders": [
            {
                "order_id": DEMO_ORDER["order_id"],
                "sku": item.sku,
                "name": item.name,
                "price": item.base_price,
                "delivered_days_ago": 18,
                "returnable": True,
            }
        ]
    }
