from __future__ import annotations

"""
Buy Stars via https://api.fragment-api.space
Seed MUST be Base64(utf-8 mnemonic words), not plain text.
"""

from __future__ import annotations

import asyncio
import base64
import json
from typing import Any
from uuid import UUID

import httpx

from app.config import Settings
from app.integrations.fragment.base import (
    HealthStatus,
    PurchaseResult,
    Quote,
    Recipient,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


def encode_seed(mnemonic: str) -> str:
    """API requires Base64-encoded seed string (mnemonic words)."""
    raw = mnemonic.strip()
    # already base64?
    try:
        decoded = base64.b64decode(raw, validate=True)
        if decoded and (b" " in decoded or len(decoded) >= 16):
            return raw  # already b64
    except Exception:
        pass
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")


class FragmentApiSpaceClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base = (settings.fragment_api_base or "https://api.fragment-api.space").rstrip("/")
        self._seed_raw = settings.ton_mnemonic.get_secret_value().strip()
        self._seed_b64 = encode_seed(self._seed_raw) if self._seed_raw else ""
        self._client = httpx.AsyncClient(timeout=90.0)

    @property
    def enabled(self) -> bool:
        return bool(self._seed_raw)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def check_recipient(self, username: str) -> Recipient | None:
        clean = username.lstrip("@").lower()
        if len(clean) < 4:
            return None
        return Recipient(username=clean)

    async def get_quote(self, stars: int) -> Quote:
        try:
            r = await self._client.get(f"{self._base}/api/v1/prices")
            r.raise_for_status()
            data = r.json()
            stars_block = data.get("stars") if isinstance(data, dict) else None
            per = 0.013
            if isinstance(stars_block, dict):
                per = float(
                    stars_block.get("price_per_star_ton")
                    or stars_block.get("price_with_commission_no_kyc")
                    or per
                )
            nano = int(float(per) * stars * 1_000_000_000)
            return Quote(stars=stars, amount_nano=nano, raw=data if isinstance(data, dict) else None)
        except Exception:
            nano = int(self._settings.star_price_ton * stars * 1_000_000_000)
            return Quote(stars=stars, amount_nano=nano)

    async def buy_stars(self, order_id: UUID, username: str, stars: int) -> PurchaseResult:
        if not self._seed_b64:
            return PurchaseResult(success=False, error="TON_MNEMONIC not set in env")

        uname = username if username.startswith("@") else f"@{username}"
        body: dict[str, Any] = {
            "username": uname,
            "amount": int(stars),
            "seed": self._seed_b64,
            "payment_method": "ton",
        }
        # optional v4r2 / v5r1 hints from env
        version = getattr(self._settings, "ton_wallet_version", "v4r2")
        if version:
            body["wallet_version"] = version

        cookies = self._settings.fragment_cookies.get_secret_value().strip()
        if cookies:
            # API expects base64 cookies JSON
            try:
                base64.b64decode(cookies, validate=True)
                body["fragment_cookies"] = cookies
            except Exception:
                body["fragment_cookies"] = base64.b64encode(cookies.encode()).decode()

        print(
            f"[fragment] buy start order={order_id} user={uname} stars={stars}",
            flush=True,
        )
        try:
            r = await self._client.post(f"{self._base}/api/v1/stars/buy", json=body)
            text = r.text
            try:
                data = r.json()
            except Exception:
                data = {"raw": text[:500]}

            print(f"[fragment] buy http={r.status_code} body={text[:400]}", flush=True)

            if r.status_code >= 400 or data.get("success") is False:
                err = self._format_error(data, r.status_code)
                return PurchaseResult(success=False, error=err)

            request_id = None
            if isinstance(data.get("data"), dict):
                request_id = data["data"].get("request_id") or data["data"].get("id")
            request_id = request_id or data.get("request_id") or data.get("purchase_id") or data.get("id")

            if not request_id:
                if data.get("success") or str(data.get("status", "")).lower() in {
                    "completed",
                    "success",
                }:
                    return PurchaseResult(
                        success=True,
                        ref_id=str(order_id),
                        tx_hash=str(
                            data.get("transaction_hash")
                            or data.get("tx_hash")
                            or ""
                        )
                        or None,
                    )
                return PurchaseResult(
                    success=False,
                    error=f"no request_id in response: {json.dumps(data)[:300]}",
                )

            return await self._poll(str(request_id))
        except Exception as exc:
            print(f"[fragment] buy exception: {exc}", flush=True)
            return PurchaseResult(success=False, error=str(exc))

    def _format_error(self, data: Any, status: int) -> str:
        if not isinstance(data, dict):
            return f"HTTP {status}: {data}"
        err = data.get("error")
        if isinstance(err, dict):
            msg = err.get("message") or err.get("error_code") or str(err)
            details = err.get("details")
            if details:
                msg = f"{msg} | {details}"
            return str(msg)[:400]
        return str(data.get("message") or data.get("error") or data)[:400]

    async def _poll(self, request_id: str, attempts: int = 45, delay: float = 3.0) -> PurchaseResult:
        print(f"[fragment] poll {request_id}", flush=True)
        for i in range(attempts):
            await asyncio.sleep(delay)
            try:
                r = await self._client.get(f"{self._base}/api/v1/queue/{request_id}")
                data = r.json() if r.content else {}
            except Exception as exc:
                print(f"[fragment] poll error: {exc}", flush=True)
                continue

            payload = data.get("data") if isinstance(data.get("data"), dict) else data
            if not isinstance(payload, dict):
                payload = data if isinstance(data, dict) else {}

            status = str(
                payload.get("status") or payload.get("state") or data.get("status") or ""
            ).lower()
            print(f"[fragment] poll#{i} status={status}", flush=True)

            if status in {"completed", "success", "done"}:
                result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
                return PurchaseResult(
                    success=True,
                    ref_id=request_id,
                    tx_hash=str(
                        payload.get("transaction_hash")
                        or payload.get("tx_hash")
                        or (result or {}).get("transaction_hash")
                        or ""
                    )
                    or None,
                )
            if status in {"failed", "error", "timeout", "cancelled"}:
                err = (
                    payload.get("error")
                    or payload.get("message")
                    or (payload.get("result") or {}).get("error")
                    if isinstance(payload.get("result"), dict)
                    else None
                )
                return PurchaseResult(
                    success=False,
                    ref_id=request_id,
                    error=str(err or status)[:400],
                )
        return PurchaseResult(success=False, ref_id=request_id, error="poll_timeout (~2 min)")

    async def get_wallet_balance(self) -> int:
        return 0

    async def healthcheck(self) -> HealthStatus:
        try:
            r = await self._client.get(f"{self._base}/health")
            return HealthStatus(ok=r.status_code == 200 and self.enabled, message=r.text[:100])
        except Exception as exc:
            return HealthStatus(ok=False, message=str(exc))
