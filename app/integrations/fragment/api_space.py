from __future__ import annotations

"""
Auto-buy Stars via public Fragment proxy API (api.fragment-api.space).
Uses YOUR TON wallet seed from env — top up that wallet, service spends it.
Docs: https://github.com/bbbuilt/fragment-stars-api
"""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

import httpx

from app.config import Settings
from app.integrations.fragment.base import (
    FragmentClient,
    HealthStatus,
    PurchaseResult,
    Quote,
    Recipient,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class FragmentApiSpaceClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base = settings.fragment_api_base.rstrip("/")
        self._seed = settings.ton_mnemonic.get_secret_value().strip()
        self._client = httpx.AsyncClient(timeout=60.0)

    @property
    def enabled(self) -> bool:
        return bool(self._seed)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def check_recipient(self, username: str) -> Recipient | None:
        # API has no dedicated search; accept username format, buy will fail if invalid
        clean = username.lstrip("@").lower()
        if len(clean) < 5:
            return None
        return Recipient(username=clean)

    async def get_quote(self, stars: int) -> Quote:
        try:
            r = await self._client.get(f"{self._base}/api/v1/prices")
            r.raise_for_status()
            data = r.json()
            # best-effort parse
            per = float(
                data.get("stars_ton")
                or data.get("star_price_ton")
                or data.get("ton_per_star")
                or 0.013
            )
            nano = int(per * stars * 1_000_000_000)
            return Quote(stars=stars, amount_nano=nano, raw=data if isinstance(data, dict) else None)
        except Exception:
            nano = int(self._settings.star_price_ton * stars * 1_000_000_000)
            return Quote(stars=stars, amount_nano=nano)

    async def buy_stars(self, order_id: UUID, username: str, stars: int) -> PurchaseResult:
        if not self._seed:
            return PurchaseResult(success=False, error="TON_MNEMONIC not set")

        body: dict[str, Any] = {
            "username": username if username.startswith("@") else f"@{username}",
            "amount": stars,
            "seed": self._seed,
            "payment_method": "ton",
        }
        cookies = self._settings.fragment_cookies.get_secret_value().strip()
        if cookies:
            body["fragment_cookies"] = cookies

        logger.info("fragment_buy_start", order_id=str(order_id), username=username, stars=stars)
        try:
            r = await self._client.post(f"{self._base}/api/v1/stars/buy", json=body)
            data = r.json() if r.content else {}
            if r.status_code >= 400:
                err = data.get("error") or data.get("message") or r.text[:200]
                return PurchaseResult(success=False, error=str(err))

            # normalize response shapes
            request_id = (
                (data.get("data") or {}).get("request_id")
                if isinstance(data.get("data"), dict)
                else None
            ) or data.get("request_id") or data.get("purchase_id") or data.get("id")

            if not request_id:
                # some APIs complete inline
                if data.get("success") or data.get("status") == "completed":
                    return PurchaseResult(
                        success=True,
                        ref_id=str(order_id),
                        tx_hash=data.get("transaction_hash") or data.get("tx_hash"),
                    )
                return PurchaseResult(success=False, error=f"unexpected response: {data}")

            # poll queue
            final = await self._poll(str(request_id))
            return final
        except Exception as exc:
            logger.exception("fragment_buy_error", error=str(exc))
            return PurchaseResult(success=False, error=str(exc))

    async def _poll(self, request_id: str, attempts: int = 40, delay: float = 3.0) -> PurchaseResult:
        for _ in range(attempts):
            await asyncio.sleep(delay)
            try:
                r = await self._client.get(f"{self._base}/api/v1/queue/{request_id}")
                data = r.json() if r.content else {}
            except Exception:
                continue
            # unwrap
            payload = data.get("data") if isinstance(data.get("data"), dict) else data
            status = str(
                payload.get("status") or payload.get("state") or data.get("status") or ""
            ).lower()
            if status in {"completed", "success", "done"}:
                return PurchaseResult(
                    success=True,
                    ref_id=request_id,
                    tx_hash=payload.get("transaction_hash")
                    or payload.get("tx_hash")
                    or payload.get("hash"),
                )
            if status in {"failed", "error", "timeout", "cancelled"}:
                return PurchaseResult(
                    success=False,
                    ref_id=request_id,
                    error=str(payload.get("error") or payload.get("message") or status),
                )
        return PurchaseResult(success=False, ref_id=request_id, error="poll_timeout")

    async def get_wallet_balance(self) -> int:
        return 0  # not provided by this API reliably

    async def healthcheck(self) -> HealthStatus:
        try:
            r = await self._client.get(f"{self._base}/health")
            ok = r.status_code == 200
            return HealthStatus(ok=ok and self.enabled, message="api.fragment-api.space")
        except Exception as exc:
            return HealthStatus(ok=False, message=str(exc))


_: FragmentClient = FragmentApiSpaceClient  # type: ignore[assignment, misc]
