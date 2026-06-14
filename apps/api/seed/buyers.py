"""~12 seeded buyers on the demand waitlist, clustered around Patiala so the
match map has pulsing pins and the winning buyer lands ~4 km away (Section 9 / 2.9).
"""
from __future__ import annotations

from domain.models import Buyer, Grade, WishlistEntry

# Centre: Patiala 30.3398, 76.3869
BUYERS: list[Buyer] = [
    Buyer(
        id="buyer_rohan",
        name="Rohan",
        lat=30.3070, lng=76.4100,  # ~4.2 km from seller — the demo hero match
        wishlist=[WishlistEntry(sku="SKU-HP-01", max_price=4500, condition_min=Grade.C)],
    ),
    Buyer(
        id="buyer_meera", name="Meera", lat=30.3502, lng=76.3601,
        wishlist=[WishlistEntry(sku="SKU-HP-01", max_price=3800, condition_min=Grade.B)],
    ),
    Buyer(
        id="buyer_arjun", name="Arjun", lat=30.3705, lng=76.4221,
        wishlist=[WishlistEntry(sku="SKU-HP-01", max_price=5000, condition_min=Grade.C)],
    ),
    Buyer(
        id="buyer_kavya", name="Kavya", lat=30.3088, lng=76.3502,
        wishlist=[WishlistEntry(sku="SKU-SH-01", max_price=4000, condition_min=Grade.B)],
    ),
    Buyer(
        id="buyer_dev", name="Dev", lat=30.3601, lng=76.3990,
        wishlist=[WishlistEntry(sku="SKU-HP-01", max_price=4000, condition_min=Grade.B)],
    ),
    Buyer(
        id="buyer_isha", name="Isha", lat=30.2950, lng=76.4100,
        wishlist=[WishlistEntry(sku="SKU-AP-01", max_price=3000, condition_min=Grade.C)],
    ),
    Buyer(
        id="buyer_vikram", name="Vikram", lat=30.3810, lng=76.3700,
        wishlist=[WishlistEntry(sku="SKU-HP-01", max_price=4600, condition_min=Grade.C)],
    ),
    Buyer(
        id="buyer_nisha", name="Nisha", lat=30.3300, lng=76.3300,
        wishlist=[WishlistEntry(sku="SKU-SH-01", max_price=3500, condition_min=Grade.C)],
    ),
    Buyer(
        id="buyer_aman", name="Aman", lat=30.3155, lng=76.3820,
        wishlist=[WishlistEntry(sku="SKU-HP-01", max_price=4050, condition_min=Grade.C)],
    ),
    Buyer(
        id="buyer_priya", name="Priya", lat=30.3450, lng=76.4300,
        wishlist=[WishlistEntry(sku="SKU-AP-01", max_price=2800, condition_min=Grade.B)],
    ),
    Buyer(
        id="buyer_sahil", name="Sahil", lat=30.3000, lng=76.3650,
        wishlist=[WishlistEntry(sku="SKU-HP-01", max_price=3900, condition_min=Grade.A)],
    ),
    Buyer(
        id="buyer_tara", name="Tara", lat=30.3550, lng=76.4150,
        wishlist=[WishlistEntry(sku="SKU-SH-01", max_price=4200, condition_min=Grade.C)],
    ),
]
