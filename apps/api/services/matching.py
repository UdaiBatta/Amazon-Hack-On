"""Buyer matching: haversine over the seeded demand waitlist (Section 2.9).

Real logic, seeded data. Production = OpenSearch geo + vector similarity.
Rank by distance × price fit × condition fit.
"""
from __future__ import annotations

import math

from domain.models import Buyer, Grade
from domain.store import store

_GRADE_ORDER = {Grade.D: 0, Grade.C: 1, Grade.B: 2, Grade.A: 3}


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    )
    return round(2 * r * math.asin(math.sqrt(a)), 2)


def find_matches(
    sku: str,
    grade: Grade,
    resale_price: float,
    seller_lat: float,
    seller_lng: float,
    limit: int = 5,
) -> list[dict]:
    candidates: list[dict] = []
    for buyer in store.buyers:
        for entry in buyer.wishlist:
            if entry.sku != sku:
                continue
            if resale_price > entry.max_price:
                continue
            if _GRADE_ORDER[grade] < _GRADE_ORDER[entry.condition_min]:
                continue
            dist = haversine_km(seller_lat, seller_lng, buyer.lat, buyer.lng)
            price_fit = max(0.0, 1.0 - (resale_price / entry.max_price) * 0.5)
            # proximity dominates for a local relay; price headroom breaks ties
            rank = (1.0 / (1.0 + dist)) * 0.85 + price_fit * 0.15
            candidates.append(
                {
                    "buyer_id": buyer.id,
                    "buyer_name": buyer.name,
                    "lat": buyer.lat,
                    "lng": buyer.lng,
                    "distance_km": dist,
                    "max_price": entry.max_price,
                    "condition_min": entry.condition_min.value,
                    "fit": round(rank, 4),
                }
            )
            break
    candidates.sort(key=lambda c: c["fit"], reverse=True)
    return candidates[:limit]


def demand_pins(sku: str) -> list[dict]:
    """All waitlist pins for this SKU — the pulsing demand pins on the map."""
    pins = []
    for buyer in store.buyers:
        if any(e.sku == sku for e in buyer.wishlist):
            pins.append({"buyer_id": buyer.id, "lat": buyer.lat, "lng": buyer.lng})
    return pins
