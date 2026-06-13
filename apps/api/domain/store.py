"""In-memory store behind a repository interface.

Chosen for max demo stability + zero AWS friction. Same access patterns as the
DynamoDB single-table design (PK=SESSION#id), so swapping to Dynamo is a
repository implementation, not a redesign.
"""
from __future__ import annotations

from domain.models import Buyer, Event, Item, ReturnSession, Transfer
from seed.buyers import BUYERS
from seed.catalog import CATALOG


class Store:
    def __init__(self) -> None:
        self.items: dict[str, Item] = dict(CATALOG)
        self.buyers: list[Buyer] = list(BUYERS)
        self.sessions: dict[str, ReturnSession] = {}
        self.frame_bytes: dict[str, list[bytes]] = {}  # raw scan frames for live AI
        self.events: list[Event] = []
        self.transfers: dict[str, Transfer] = {}

    # --- items -----------------------------------------------------------
    def get_item(self, sku: str) -> Item | None:
        return self.items.get(sku)

    # --- sessions --------------------------------------------------------
    def put_session(self, session: ReturnSession) -> ReturnSession:
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> ReturnSession | None:
        return self.sessions.get(session_id)

    # --- events (append-only custody ledger) -----------------------------
    def append_event(self, event: Event) -> Event:
        self.events.append(event)
        return event

    def events_for(self, session_id: str | None = None) -> list[Event]:
        if session_id is None:
            return list(self.events)
        return [e for e in self.events if e.session_id == session_id]

    # --- transfers -------------------------------------------------------
    def put_transfer(self, transfer: Transfer) -> Transfer:
        self.transfers[transfer.id] = transfer
        return transfer

    def get_transfer(self, transfer_id: str) -> Transfer | None:
        return self.transfers.get(transfer_id)


# Single process-wide instance.
store = Store()
