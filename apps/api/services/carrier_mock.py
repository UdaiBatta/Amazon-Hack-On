"""Mocked carrier behind a REAL interface (Section 5.2 / honest mock pattern).

Returns a fake-but-well-formed booking. Production swaps the implementation for
Shiprocket / Delhivery / UPS. The MOCK badge surfaces in the ops dashboard only.
"""
from __future__ import annotations

import random
import string
from typing import Protocol

from domain.models import Transfer


class CarrierService(Protocol):
    def book(self, session_id: str, buyer_id: str) -> Transfer: ...


class MockCarrier:
    MOCK = True

    def book(self, session_id: str, buyer_id: str) -> Transfer:
        tracking = "RLY" + "".join(random.choices(string.digits, k=10))
        return Transfer(
            session_id=session_id,
            buyer_id=buyer_id,
            label_url=f"/labels/{tracking}.png",
            tracking=tracking,
            status="reserved",
            mock=True,
        )


carrier: CarrierService = MockCarrier()
