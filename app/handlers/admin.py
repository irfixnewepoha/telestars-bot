from __future__ import annotations

from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.config import get_settings

router = Router(name="admin")


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        settings = get_settings()
        return bool(message.from_user and message.from_user.id in settings.admin_ids)


@router.message(AdminFilter(), lambda m: m.text and m.text.startswith("/admin"))
async def admin_stub(message: Message) -> None:
    await message.answer(
        "Админ-панель (статистика, настройки, заказы, cookies) — реализуется в фазе 7."
    )
