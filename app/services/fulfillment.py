from __future__ import annotations

import asyncio
from uuid import UUID

from aiogram import Bot

from app.config import Settings, get_settings
from app.integrations.fragment.api_space import FragmentApiSpaceClient
from app.integrations.fragment.mock import MockFragmentClient
from app.utils.logging import get_logger

logger = get_logger(__name__)

# simple in-memory lock against double fulfill for same order_id
_in_flight: set[str] = set()


def get_fragment_client(settings: Settings):
    if settings.ton_mnemonic.get_secret_value().strip():
        return FragmentApiSpaceClient(settings)
    return MockFragmentClient()


async def fulfill_stars(
    *,
    bot: Bot,
    user_id: int,
    order_id: str,
    username: str,
    stars: int,
    chat_id: int | None = None,
) -> bool:
    """
    Buy stars on Fragment and notify user.
    Returns True on success.
    """
    if order_id in _in_flight:
        logger.warning("fulfill_already_in_flight", order_id=order_id)
        return False
    _in_flight.add(order_id)

    settings = get_settings()
    client = get_fragment_client(settings)
    try:
        # notify processing
        target = chat_id or user_id
        try:
            await bot.send_message(
                target,
                f"⏳ Оплата получена. Покупаем <b>{stars}</b> ⭐ для @{username}…",
            )
        except Exception:
            pass

        result = await client.buy_stars(UUID(order_id) if _is_uuid(order_id) else UUID(int=0), username, stars)

        if result.success:
            text = (
                f"✅ <b>Готово!</b>\n\n"
                f"⭐ <b>{stars}</b> отправлено на @{username}\n"
            )
            if result.tx_hash:
                text += f"\nTx: <code>{result.tx_hash}</code>"
            try:
                await bot.send_message(target, text)
            except Exception:
                pass
            for admin_id in settings.admin_ids:
                try:
                    await bot.send_message(
                        admin_id,
                        f"✅ Выдача OK\n⭐ {stars} → @{username}\norder={order_id}\n"
                        f"ref={result.ref_id} tx={result.tx_hash}",
                    )
                except Exception:
                    pass
            logger.info("fulfill_ok", order_id=order_id, username=username, stars=stars)
            return True

        err = result.error or "unknown"
        try:
            await bot.send_message(
                target,
                f"❌ Не удалось автоматически выдать звёзды.\n"
                f"Причина: <code>{err}</code>\n"
                f"Админ уже уведомлён — разберём вручную.",
            )
        except Exception:
            pass
        for admin_id in settings.admin_ids:
            try:
                await bot.send_message(
                    admin_id,
                    f"❌ Выдача FAILED\n⭐ {stars} → @{username}\norder={order_id}\n{err}\n"
                    f"Проверьте баланс TON на кошельке Fragment / TON_MNEMONIC.",
                )
            except Exception:
                pass
        logger.error("fulfill_fail", order_id=order_id, error=err)
        return False
    finally:
        _in_flight.discard(order_id)
        close = getattr(client, "aclose", None)
        if close:
            await close()


def _is_uuid(s: str) -> bool:
    try:
        UUID(s)
        return True
    except Exception:
        return False


def schedule_fulfill(
    bot: Bot,
    *,
    user_id: int,
    order_id: str,
    username: str,
    stars: int,
    chat_id: int | None = None,
) -> None:
    """Fire-and-forget background task."""
    asyncio.create_task(
        fulfill_stars(
            bot=bot,
            user_id=user_id,
            order_id=order_id,
            username=username,
            stars=stars,
            chat_id=chat_id,
        )
    )
