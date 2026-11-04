from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import get_settings
from app.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


async def _build_storage():
    settings = get_settings()
    try:
        from aiogram.fsm.storage.redis import RedisStorage
        from redis.asyncio import Redis

        redis = Redis.from_url(settings.redis_url)
        await redis.ping()
        logger.info("fsm_storage", backend="redis")
        return RedisStorage(redis=redis)
    except Exception as exc:
        logger.warning("redis_unavailable_fallback_memory", error=str(exc))
        return MemoryStorage()


async def main() -> None:
    setup_logging()
    settings = get_settings()

    if not settings.bot_token.get_secret_value() or settings.bot_token.get_secret_value().startswith("123456"):
        logger.error("BOT_TOKEN is missing or placeholder — set it in environment")
        raise SystemExit(1)

    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = await _build_storage()
    dp = Dispatcher(storage=storage)

    from app.handlers import setup_routers

    setup_routers(dp)

    use_polling = settings.use_polling or not settings.webhook_host
    logger.info(
        "starting_bot",
        mode="polling" if use_polling else "webhook",
        brand=settings.brand_name,
    )

    if use_polling:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    else:
        from aiohttp import web

        from app.integrations.platega.webhook import setup_platega_webhook

        # Simple health for Railway
        async def health(_request: web.Request) -> web.Response:
            return web.json_response({"status": "ok"})

        app = web.Application()
        app.router.add_get("/health", health)
        app.router.add_get("/", health)
        setup_platega_webhook(app)

        # Telegram webhook can be set externally; polling is recommended for first Railway deploy
        port = int(os.environ.get("PORT", "8080"))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info("http_server_started", port=port)
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
