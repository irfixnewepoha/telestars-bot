from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import Settings
from app.integrations.platega.schemas import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    TransactionStatusResponse,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PlategaClient:
    def __init__(self, settings: Settings) -> None:
        self._base = settings.platega_base_url.rstrip("/")
        self._merchant_id = settings.platega_merchant_id
        self._secret = settings.platega_secret.get_secret_value()
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(20.0, connect=10.0),
            headers={
                "Content-Type": "application/json",
                "X-MerchantId": self._merchant_id,
                "X-Secret": self._secret,
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def create_payment(self, req: CreatePaymentRequest) -> CreatePaymentResponse:
        body: dict[str, Any] = {
            "paymentMethod": req.payment_method,
            "paymentDetails": {
                "amount": req.amount,
                "currency": req.currency,
            },
            "description": req.description,
            "return": req.return_url,
            "failedUrl": req.failed_url,
        }
        if req.payload:
            body["payload"] = req.payload
        if req.metadata:
            body["metadata"] = req.metadata

        logger.info("platega_create_payment", amount=req.amount, payload=req.payload)
        resp = await self._client.post(f"{self._base}/transaction/process", json=body)
        resp.raise_for_status()
        data = resp.json()
        return CreatePaymentResponse.model_validate(data)

    async def get_status(self, transaction_id: str) -> TransactionStatusResponse:
        resp = await self._client.get(f"{self._base}/transaction/{transaction_id}")
        resp.raise_for_status()
        data = resp.json()
        # Normalize id field if present under different keys
        if "id" not in data and "transactionId" in data:
            data["id"] = data["transactionId"]
        return TransactionStatusResponse.model_validate(data)
