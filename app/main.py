from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import get_settings
from app.utils.logging import get_logger, setup_logging


async def _build_storage():
    settings = get_settings()
    log = get_logger("main")
    try:
        from aiogram.fsm.storage.redis import RedisStorage
        from redis.asyncio import Redis

        redis = Redis.from_url(settings.redis_url, socket_connect_timeout=5)
        await redis.ping()
        log.info("fsm_storage", backend="redis")
        return RedisStorage(redis=redis)
    except Exception as exc:
        # Fallback: bot still works, FSM only in memory
        try:
            log.warning("redis_unavailable_fallback_memory", error=str(exc))
        except Exception:
            print(f"redis unavailable, using MemoryStorage: {exc}", flush=True)
        return MemoryStorage()


async def main() -> None:
    setup_logging()
    log = get_logger("main")
    settings = get_settings()

    token = settings.bot_token.get_secret_value()
    if not token or token.startswith("123456"):
        print("BOT_TOKEN is missing — set it in Railway Variables", flush=True)
        raise SystemExit(1)

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = await _build_storage()
    dp = Dispatcher(storage=storage)

    from app.handlers import setup_routers

    setup_routers(dp)

    use_polling = settings.use_polling or not settings.webhook_host
    log.info(
        "starting_bot",
        mode="polling" if use_polling else "webhook",
        brand=settings.brand_name,
        platega=settings.platega_enabled,
        cryptobot=settings.cryptobot_enabled,
        fragment_seed=bool(settings.ton_mnemonic.get_secret_value().strip()),
    )

    if use_polling:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    else:
        from aiohttp import web

        from app.integrations.platega.webhook import setup_platega_webhook

        async def health(_request: web.Request) -> web.Response:
            return web.json_response({"status": "ok"})

        app = web.Application()
        app.router.add_get("/health", health)
        app.router.add_get("/", health)
        setup_platega_webhook(app)

        port = int(os.environ.get("PORT", "8080"))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        log.info("http_server_started", port=port)
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
