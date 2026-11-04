from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class CryptoBotClient:
    """Crypto Pay API (@CryptoBot). Docs: https://help.crypt.bot/crypto-pay-api"""

    def __init__(self, settings: Settings) -> None:
        self._token = settings.cryptobot_token.get_secret_value()
        base = (
            "https://testnet-pay.crypt.bot/api"
            if settings.cryptobot_testnet
            else "https://pay.crypt.bot/api"
        )
        self._base = base
        self._client = httpx.AsyncClient(
            timeout=20.0,
            headers={"Crypto-Pay-API-Token": self._token},
        )

    @property
    def enabled(self) -> bool:
        return bool(self._token)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_me(self) -> dict[str, Any]:
        return await self._request("getMe")

    async def create_invoice(
        self,
        *,
        amount: str,
        asset: str = "TON",
        description: str,
        payload: str,
        expires_in: int = 900,
    ) -> dict[str, Any]:
        """Create invoice. amount as string, e.g. '0.5'."""
        params: dict[str, Any] = {
            "asset": asset,
            "amount": amount,
            "description": description[:1024],
            "payload": payload[:1024],
            "expires_in": expires_in,
            "allow_comments": False,
            "allow_anonymous": True,
        }
        result = await self._request("createInvoice", params)
        logger.info("cryptobot_invoice_created", invoice_id=result.get("invoice_id"))
        return result

    async def get_invoices(
        self,
        *,
        invoice_ids: list[int] | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if invoice_ids:
            params["invoice_ids"] = ",".join(str(i) for i in invoice_ids)
        if status:
            params["status"] = status
        result = await self._request("getInvoices", params)
        if isinstance(result, list):
            return result
        return result.get("items", []) if isinstance(result, dict) else []

    async def get_balance(self) -> list[dict[str, Any]]:
        result = await self._request("getBalance")
        return result if isinstance(result, list) else []

    async def _request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        if not self._token:
            raise RuntimeError("CRYPTOBOT_TOKEN is not set")
        resp = await self._client.get(f"{self._base}/{method}", params=params or {})
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            raise RuntimeError(f"CryptoBot error: {data}")
        return data.get("result")
