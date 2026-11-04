from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

from app.integrations.fragment.base import (
    FragmentClient,
    HealthStatus,
    PurchaseResult,
    Quote,
    Recipient,
)


class MockFragmentClient:
    """In-memory mock for tests and local development."""

    def __init__(
        self,
        *,
        known_users: dict[str, str] | None = None,
        price_per_star_nano: int = 15_000_000,  # ~0.015 TON
        wallet_balance_nano: int = 10_000_000_000,  # 10 TON
        fail_buy: bool = False,
    ) -> None:
        self._known = known_users or {
            "durov": "Pavel Durov",
            "telegram": "Telegram",
            "testuser": "Test User",
        }
        self._price = price_per_star_nano
        self._balance = wallet_balance_nano
        self._fail_buy = fail_buy
        self._purchases: list[dict] = []

    async def check_recipient(self, username: str) -> Recipient | None:
        await asyncio.sleep(0.01)
        clean = username.lstrip("@").lower()
        if clean in self._known:
            return Recipient(username=clean, name=self._known[clean])
        return None

    async def get_quote(self, stars: int) -> Quote:
        await asyncio.sleep(0.01)
        return Quote(stars=stars, amount_nano=stars * self._price)

    async def buy_stars(self, order_id: UUID, username: str, stars: int) -> PurchaseResult:
        await asyncio.sleep(0.05)
        if self._fail_buy:
            return PurchaseResult(success=False, error="mock_failure")
        cost = stars * self._price
        if cost > self._balance:
            return PurchaseResult(success=False, error="insufficient_balance")
        self._balance -= cost
        ref = f"mock-{uuid4().hex[:12]}"
        tx = f"txmock{uuid4().hex[:16]}"
        self._purchases.append(
            {"order_id": str(order_id), "username": username, "stars": stars, "ref": ref}
        )
        return PurchaseResult(success=True, ref_id=ref, tx_hash=tx, cost_nano=cost)

    async def get_wallet_balance(self) -> int:
        return self._balance

    async def healthcheck(self) -> HealthStatus:
        return HealthStatus(ok=True, message="mock ok", wallet_balance_nano=self._balance)


# Type check helper
_: FragmentClient = MockFragmentClient()  # type: ignore[assignment]
