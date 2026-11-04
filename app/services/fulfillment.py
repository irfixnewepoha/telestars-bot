from __future__ import annotations

import asyncio
import traceback
from uuid import UUID

from aiogram import Bot

from app.config import Settings, get_settings
from app.integrations.fragment.api_space import FragmentApiSpaceClient
from app.utils.logging import get_logger

logger = get_logger(__name__)
_in_flight: set[str] = set()


def get_fragment_client(settings: Settings) -> FragmentApiSpaceClient:
    # Always real client path — mock only hides production bugs
    return FragmentApiSpaceClient(settings)


async def fulfill_stars(
    *,
    bot: Bot,
    user_id: int,
    order_id: str,
    username: str,
    stars: int,
    chat_id: int | None = None,
) -> bool:
    if order_id in _in_flight:
        print(f"[fulfill] skip in-flight {order_id}", flush=True)
        return False
    _in_flight.add(order_id)

    settings = get_settings()
    target = chat_id or user_id
    client = get_fragment_client(settings)

    try:
        seed_ok = bool(settings.ton_mnemonic.get_secret_value().strip())
        print(
            f"[fulfill] start order={order_id} @{username} stars={stars} seed_set={seed_ok}",
            flush=True,
        )

        if not seed_ok:
            msg = (
                "❌ Автовыдача не настроена: в Railway нет <code>TON_MNEMONIC</code>.\n"
                "Добавьте 24 слова кошелька с TON (баланс ≥ 1 TON)."
            )
            await _safe_send(bot, target, msg)
            await _notify_admins(bot, settings, f"❌ Нет TON_MNEMONIC\n⭐ {stars} → @{username}")
            return False

        await _safe_send(
            bot,
            target,
            f"⏳ Покупаем <b>{stars}</b> ⭐ для @{username} через Fragment…",
        )

        oid = UUID(order_id) if _is_uuid(order_id) else UUID(int=0)
        result = await client.buy_stars(oid, username, stars)
        print(f"[fulfill] result success={result.success} err={result.error}", flush=True)

        if result.success:
            text = f"✅ <b>Готово!</b>\n\n⭐ <b>{stars}</b> → @{username}"
            if result.tx_hash:
                text += f"\nTx: <code>{result.tx_hash}</code>"
            await _safe_send(bot, target, text)
            await _notify_admins(
                bot,
                settings,
                f"✅ Выдача OK\n⭐ {stars} → @{username}\norder={order_id}\nref={result.ref_id}",
            )
            return True

        err = result.error or "unknown"
        await _safe_send(
            bot,
            target,
            f"❌ Не удалось выдать звёзды автоматически.\nПричина: <code>{err}</code>\n"
            f"Админ уведомлён.",
        )
        await _notify_admins(
            bot,
            settings,
            f"❌ Выдача FAILED\n⭐ {stars} → @{username}\norder={order_id}\n{err}\n"
            f"Проверьте: баланс ≥1 TON, TON_MNEMONIC верный, кошелёк V4R2.",
        )
        return False
    except Exception as exc:
        print(f"[fulfill] exception: {exc}\n{traceback.format_exc()}", flush=True)
        await _safe_send(bot, target, f"❌ Ошибка выдачи: <code>{exc}</code>")
        await _notify_admins(bot, settings, f"❌ exception fulfill: {exc}")
        return False
    finally:
        _in_flight.discard(order_id)
        try:
            await client.aclose()
        except Exception:
            pass


async def _safe_send(bot: Bot, chat_id: int, text: str) -> None:
    try:
        await bot.send_message(chat_id, text)
    except Exception as exc:
        print(f"[fulfill] send fail chat={chat_id}: {exc}", flush=True)


async def _notify_admins(bot: Bot, settings: Settings, text: str) -> None:
    for admin_id in settings.admin_ids:
        await _safe_send(bot, admin_id, text)


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
    async def _runner() -> None:
        try:
            await fulfill_stars(
                bot=bot,
                user_id=user_id,
                order_id=order_id,
                username=username,
                stars=stars,
                chat_id=chat_id,
            )
        except Exception as exc:
            print(f"[fulfill] task crash: {exc}", flush=True)

    asyncio.create_task(_runner())
