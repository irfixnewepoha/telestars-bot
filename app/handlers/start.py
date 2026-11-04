from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import get_settings
from app.keyboards.inline import coming_soon_kb, main_menu
from app.texts import ru as t

router = Router(name="start")


async def _show_home(message: Message | None, edit: bool = False) -> None:
    text = t.WELCOME.format(brand=t.brand())
    kb = main_menu()
    if message is None:
        return
    if edit:
        try:
            await message.edit_text(text, reply_markup=kb)
            return
        except Exception:
            pass
    await message.answer(text, reply_markup=kb)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    # TODO: upsert user in DB
    await _show_home(message, edit=False)


@router.callback_query(F.data == "menu:home")
async def cb_home(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await _show_home(callback.message, edit=True)
    await callback.answer()


@router.callback_query(F.data == "menu:premium")
async def menu_premium(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_text(t.PREMIUM_STUB, reply_markup=coming_soon_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:gifts")
async def menu_gifts(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_text(t.GIFTS_STUB, reply_markup=coming_soon_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:gram")
async def menu_gram(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_text(t.GRAM_STUB, reply_markup=coming_soon_kb())
    await callback.answer()
