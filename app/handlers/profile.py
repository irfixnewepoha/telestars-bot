from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.inline import coming_soon_kb, home_only, profile_kb
from app.texts import ru as t

router = Router(name="profile")


@router.callback_query(F.data == "menu:profile")
async def menu_profile(callback: CallbackQuery) -> None:
    user = callback.from_user
    text = t.PROFILE.format(
        user_id=user.id if user else 0,
        username=(user.username or "—") if user else "—",
        balance_rub=0.0,
        premium_months=0,
        stars_bought=0,
        gram_bought=0,
        gifts_bought=0,
        stars_sold=0,
        spent_rub=0.0,
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=profile_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("profile:history:"))
async def profile_history(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text(
            "История заказов пока пуста.", reply_markup=home_only()
        )
    await callback.answer()


@router.callback_query(F.data == "profile:referral")
async def profile_referral(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text(t.REFERRAL_STUB, reply_markup=coming_soon_kb())
    await callback.answer()


@router.callback_query(F.data == "profile:promo")
async def profile_promo(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text(t.PROMO_STUB, reply_markup=coming_soon_kb())
    await callback.answer()


@router.callback_query(F.data == "profile:lang")
async def profile_lang(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text(t.LANG_STUB, reply_markup=coming_soon_kb())
    await callback.answer()
