from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Recipient:
    username: str
    name: str | None = None
    photo_url: str | None = None


@dataclass(frozen=True, slots=True)
class Quote:
    stars: int
    amount_nano: int  # TON in nanotons
    raw: dict | None = None


@dataclass(frozen=True, slots=True)
class PurchaseResult:
    success: bool
    ref_id: str | None = None
    tx_hash: str | None = None
    cost_nano: int | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class HealthStatus:
    ok: bool
    message: str = ""
    wallet_balance_nano: int | None = None


class FragmentClient(Protocol):
    async def check_recipient(self, username: str) -> Recipient | None: ...

    async def get_quote(self, stars: int) -> Quote: ...

    async def buy_stars(
        self, order_id: UUID, username: str, stars: int
    ) -> PurchaseResult: ...

    async def get_wallet_balance(self) -> int: ...

    async def healthcheck(self) -> HealthStatus: ...
