from __future__ import annotations

"""
Real Fragment client skeleton.

IMPORTANT:
- There is no official public API for buying Stars on Fragment.
- This module must implement the flow by talking to fragment.com pages
  and signing TON transactions locally (seed never leaves the process).
- Implementation is intentionally incomplete in the initial scaffold.
  Fill in using documented open-source approaches (e.g. local signing with
  tonutils/pytoniq) and HTML fixtures for parsing tests.
- Never log or persist the mnemonic / cookies.
"""

from uuid import UUID

from app.config import Settings
from app.integrations.fragment.base import (
    FragmentClient,
    HealthStatus,
    PurchaseResult,
    Quote,
    Recipient,
)
from app.integrations.fragment.errors import FragmentUnavailable


class RealFragmentClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # TODO: initialize httpx client with realistic headers, optional proxy
        # TODO: load wallet from mnemonic (in-memory only)
        # TODO: global asyncio.Lock for sequential purchases

    async def check_recipient(self, username: str) -> Recipient | None:
        # TODO: implement search on fragment.com / API endpoints used by the site
        raise FragmentUnavailable("RealFragmentClient not fully implemented yet")

    async def get_quote(self, stars: int) -> Quote:
        raise FragmentUnavailable("RealFragmentClient not fully implemented yet")

    async def buy_stars(self, order_id: UUID, username: str, stars: int) -> PurchaseResult:
        """
        Critical safety rules (must be followed when implementing):
        1. Acquire global lock + Postgres advisory lock.
        2. Write fragment_ref_id + status=fulfilling and COMMIT before sending tx.
        3. After send, store ton_tx_hash.
        4. On restart, never re-send if ref_id/hash already present; check chain first.
        5. Only auto-retry errors that happened BEFORE the transaction was broadcast.
        """
        raise FragmentUnavailable("RealFragmentClient not fully implemented yet")

    async def get_wallet_balance(self) -> int:
        raise FragmentUnavailable("RealFragmentClient not fully implemented yet")

    async def healthcheck(self) -> HealthStatus:
        return HealthStatus(ok=False, message="RealFragmentClient not implemented")


_: FragmentClient = RealFragmentClient  # type: ignore[assignment, misc]
