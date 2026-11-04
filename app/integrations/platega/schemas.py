from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    payment_method: int = 2  # SBP QR
    amount: float  # RUB, e.g. 150.50
    currency: str = "RUB"
    description: str
    return_url: str = "https://t.me/"
    failed_url: str = "https://t.me/"
    payload: str | None = None  # order id
    metadata: dict[str, Any] | None = None


class CreatePaymentResponse(BaseModel):
    transaction_id: str = Field(alias="transactionId")
    redirect: str | None = None
    status: str
    expires_in: str | None = Field(default=None, alias="expiresIn")
    payment_method: str | None = Field(default=None, alias="paymentMethod")
    payment_details: Any = Field(default=None, alias="paymentDetails")
    merchant_id: str | None = Field(default=None, alias="merchantId")

    model_config = {"populate_by_name": True}


class TransactionStatusResponse(BaseModel):
    id: str | None = None
    status: str
    amount: float | None = None
    currency: str | None = None
    payment_method: Any = Field(default=None, alias="paymentMethod")
    # Platega may return extra / mistyped fields; keep flexible
    raw: dict[str, Any] | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}


class CallbackPayload(BaseModel):
    id: str
    amount: float
    currency: str
    status: Literal["CONFIRMED", "CANCELED", "CHARGEBACKED"]
    payment_method: int | None = Field(default=None, alias="paymentMethod")
    payload: str | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}
