from __future__ import annotations

import hmac
from typing import Any

from aiohttp import web

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def platega_callback(request: web.Request) -> web.Response:
    settings = get_settings()
    # Auth: headers must match merchant credentials
    mid = request.headers.get("X-MerchantId", "")
    secret = request.headers.get("X-Secret", "")
    if not (
        hmac.compare_digest(mid, settings.platega_merchant_id)
        and hmac.compare_digest(secret, settings.platega_secret.get_secret_value())
    ):
        logger.warning("platega_webhook_auth_failed")
        return web.Response(status=401)

    try:
        body: dict[str, Any] = await request.json()
    except Exception:
        return web.Response(status=400)

    logger.info("platega_callback", status=body.get("status"), tx_id=body.get("id"))
    # TODO: persist payment, transition order, idempotent
    return web.Response(status=200)


def setup_platega_webhook(app: web.Application) -> None:
    settings = get_settings()
    path = settings.platega_webhook_path
    app.router.add_post(path, platega_callback)
    logger.info("platega_webhook_registered", path=path)
