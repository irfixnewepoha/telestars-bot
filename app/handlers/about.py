from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.config import get_settings
from app.keyboards.inline import about_kb, home_only
from app.texts import ru as t

router = Router(name="about")


@router.callback_query(F.data == "menu:about")
async def menu_about(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text(t.ABOUT, reply_markup=about_kb())
    await callback.answer()


@router.callback_query(F.data == "about:faq")
async def about_faq(callback: CallbackQuery) -> None:
    settings = get_settings()
    if callback.message:
        await callback.message.edit_text(settings.faq_text, reply_markup=home_only())
    await callback.answer()


@router.callback_query(F.data.in_({"about:privacy", "about:terms", "about:offer", "about:support"}))
async def about_links(callback: CallbackQuery) -> None:
    settings = get_settings()
    mapping = {
        "about:privacy": settings.privacy_url or "Скоро",
        "about:terms": settings.terms_url or "Скоро",
        "about:offer": settings.offer_url or "Скоро",
        "about:support": settings.support_url or "Скоро",
    }
    url = mapping.get(callback.data or "", "Скоро")
    await callback.answer(str(url)[:200], show_alert=True)
