from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Telegram
    bot_token: SecretStr = SecretStr("")
    admin_ids: list[int] = Field(default_factory=list)
    brand_name: str = "StarsShop"

    # Database / Redis
    database_url: str = "postgresql+asyncpg://stars:stars@localhost:5432/stars_bot"
    redis_url: str = "redis://localhost:6379/0"

    # Platega (SBP)
    platega_merchant_id: str = ""
    platega_secret: SecretStr = SecretStr("")
    platega_webhook_path: str = "/webhooks/platega/secret-path-change-me"
    platega_fee_percent: float = 1.5
    platega_base_url: str = "https://app.platega.io"
    platega_return_url: str = "https://t.me/"

    # CryptoBot (Crypto Pay)
    cryptobot_token: SecretStr = SecretStr("")
    cryptobot_testnet: bool = False
    cryptobot_asset: str = "TON"
    # Approximate TON per star for invoice (override with live quote later)
    star_price_ton: float = 0.013

    # TON / Fragment
    ton_mnemonic: SecretStr = SecretStr("")
    ton_wallet_version: Literal["v4r2", "v5r1"] = "v4r2"
    fragment_cookies: SecretStr = SecretStr("")
    fragment_hash: str = ""
    fragment_proxy: str | None = None
    # Optional third-party Fragment API (like fragment-api.com) — not used by default
    fragment_api_key: str = ""
    fragment_api_base: str = "https://api.fragment-api.space"

    # Rates
    coingecko_api_key: str = ""
    star_price_rub: float = 1.5  # fixed fallback price per star in RUB

    # App behaviour
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    webhook_host: str = ""
    webhook_path: str = "/webhook/telegram"
    webhook_secret: SecretStr = SecretStr("change-me")
    use_polling: bool = True

    order_ttl_min: int = 15
    price_lock_ttl_min: int = 10
    markup_percent: float = 15.0
    min_stars: int = 50
    max_stars: int = 9999
    min_margin_kop: int = 500
    banner_file_id: str | None = None

    # Optional
    sentry_dsn: str | None = None
    support_url: str = "https://t.me/support"
    faq_text: str = "Частые вопросы появятся здесь."
    privacy_url: str = ""
    terms_url: str = ""
    offer_url: str = ""

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: object) -> list[int]:
        if isinstance(v, list):
            return [int(x) for x in v]
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return []

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_dev(self) -> bool:
        return self.environment == "development"

    @property
    def platega_enabled(self) -> bool:
        return bool(self.platega_merchant_id and self.platega_secret.get_secret_value())

    @property
    def cryptobot_enabled(self) -> bool:
        return bool(self.cryptobot_token.get_secret_value())


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
