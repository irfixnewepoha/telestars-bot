from __future__ import annotations

import uuid
from decimal import Decimal, ROUND_UP

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.config import get_settings
from app.integrations.cryptobot.client import CryptoBotClient
from app.integrations.platega.client import PlategaClient
from app.integrations.platega.schemas import CreatePaymentRequest
from app.keyboards.inline import (
    coming_soon_kb,
    stars_amount_nav,
    stars_confirm,
    stars_payment,
    stars_recipient,
    stars_section,
)
from app.texts import ru as t
from app.utils.logging import get_logger
from app.utils.validators import normalize_username, parse_stars_amount

router = Router(name="stars")
logger = get_logger(__name__)


class BuyStars(StatesGroup):
    choose_recipient = State()
    enter_amount = State()
    confirm = State()
    awaiting_payment = State()


@router.callback_query(F.data == "menu:stars")
async def menu_stars(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_text(t.STARS_SECTION, reply_markup=stars_section())
    await callback.answer()


@router.callback_query(F.data == "stars:buy")
async def stars_buy(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BuyStars.choose_recipient)
    if callback.message:
        await callback.message.edit_text(
            t.STARS_CHOOSE_RECIPIENT, reply_markup=stars_recipient()
        )
    await callback.answer()


@router.callback_query(F.data == "stars:sell")
async def stars_sell(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_text(t.SELL_STUB, reply_markup=coming_soon_kb())
    await callback.answer()


@router.callback_query(F.data == "stars:self", BuyStars.choose_recipient)
async def stars_self(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    username = (user.username or "").lower() if user else ""
    if not username:
        await callback.answer(
            "У вас нет username. Введите @username вручную.",
            show_alert=True,
        )
        return
    await state.update_data(
        recipient=username,
        recipient_name=user.full_name if user else None,
    )
    await state.set_state(BuyStars.enter_amount)
    settings = get_settings()
    text = t.STARS_ENTER_AMOUNT.format(
        username=username,
        min_stars=settings.min_stars,
        max_stars=settings.max_stars,
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=stars_amount_nav())
    await callback.answer()




@router.callback_query(F.data.startswith("stars:qty:"), BuyStars.enter_amount)
async def stars_qty_btn(callback: CallbackQuery, state: FSMContext) -> None:
    """Quick amount from keyboard."""
    try:
        amount = int((callback.data or "").split(":")[-1])
    except ValueError:
        await callback.answer("Неверное число", show_alert=True)
        return
    settings = get_settings()
    if amount < settings.min_stars or amount > settings.max_stars:
        await callback.answer("Количество вне лимита", show_alert=True)
        return
    # reuse amount flow via fake message logic
    data = await state.get_data()
    recipient = data.get("recipient", "?")
    name = data.get("recipient_name")
    name_part = f" ({name})" if name else ""
    price_rub = round(amount * settings.star_price_rub, 2)
    price_ton = float(
        (Decimal(str(amount)) * Decimal(str(settings.star_price_ton))).quantize(
            Decimal("0.0001"), rounding=ROUND_UP
        )
    )
    order_id = str(uuid.uuid4())
    await state.update_data(
        stars=amount,
        price_rub=price_rub,
        price_ton=price_ton,
        price_kop=int(round(price_rub * 100)),
        order_id=order_id,
    )
    await state.set_state(BuyStars.confirm)
    ton_s = f"{price_ton:.4f}".rstrip("0").rstrip(".")
    text = t.STARS_CONFIRM.format(
        username=recipient,
        name_part=name_part,
        stars=amount,
        price_rub=price_rub,
        price_ton=ton_s,
    )
    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=stars_confirm(
                can_sbp=settings.platega_enabled,
                can_crypto=settings.cryptobot_enabled,
            ),
        )
    await callback.answer()

@router.message(BuyStars.choose_recipient)
async def stars_username_input(message: Message, state: FSMContext) -> None:
    clean = normalize_username(message.text or "")
    if not clean:
        await message.answer(t.INVALID_USERNAME, reply_markup=stars_recipient())
        return
    await state.update_data(recipient=clean, recipient_name=None)
    await state.set_state(BuyStars.enter_amount)
    settings = get_settings()
    text = t.STARS_ENTER_AMOUNT.format(
        username=clean,
        min_stars=settings.min_stars,
        max_stars=settings.max_stars,
    )
    await message.answer(text, reply_markup=stars_amount_nav())


@router.message(BuyStars.enter_amount)
async def stars_amount_input(message: Message, state: FSMContext) -> None:
    settings = get_settings()
    amount = parse_stars_amount(
        message.text or "", settings.min_stars, settings.max_stars
    )
    if amount is None:
        await message.answer(
            t.INVALID_AMOUNT.format(
                min_stars=settings.min_stars, max_stars=settings.max_stars
            ),
            reply_markup=stars_amount_nav(),
        )
        return
    data = await state.get_data()
    recipient = data.get("recipient", "?")
    name = data.get("recipient_name")
    name_part = f" ({name})" if name else ""
    price_rub = round(amount * settings.star_price_rub, 2)
    price_ton = float(
        (Decimal(str(amount)) * Decimal(str(settings.star_price_ton))).quantize(
            Decimal("0.0001"), rounding=ROUND_UP
        )
    )
    order_id = str(uuid.uuid4())
    await state.update_data(
        stars=amount,
        price_rub=price_rub,
        price_ton=price_ton,
        price_kop=int(round(price_rub * 100)),
        order_id=order_id,
    )
    await state.set_state(BuyStars.confirm)
    ton_s = f"{price_ton:.4f}".rstrip("0").rstrip(".")
    text = t.STARS_CONFIRM.format(
        username=recipient,
        name_part=name_part,
        stars=amount,
        price_rub=price_rub,
        price_ton=ton_s,
    )
    await message.answer(
        text,
        reply_markup=stars_confirm(
            can_sbp=settings.platega_enabled,
            can_crypto=settings.cryptobot_enabled,
        ),
    )


@router.callback_query(F.data == "stars:back_recipient")
async def back_recipient(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BuyStars.choose_recipient)
    if callback.message:
        await callback.message.edit_text(
            t.STARS_CHOOSE_RECIPIENT, reply_markup=stars_recipient()
        )
    await callback.answer()


@router.callback_query(F.data == "stars:back_amount")
async def back_amount(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    recipient = data.get("recipient", "?")
    await state.set_state(BuyStars.enter_amount)
    settings = get_settings()
    text = t.STARS_ENTER_AMOUNT.format(
        username=recipient,
        min_stars=settings.min_stars,
        max_stars=settings.max_stars,
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=stars_amount_nav())
    await callback.answer()


@router.callback_query(F.data == "stars:pay:none")
async def pay_none(callback: CallbackQuery) -> None:
    await callback.answer(
        "Заполните PLATEGA_* или CRYPTOBOT_TOKEN в env на сервере.",
        show_alert=True,
    )


@router.callback_query(F.data == "stars:pay:sbp")
async def pay_sbp(callback: CallbackQuery, state: FSMContext) -> None:
    settings = get_settings()
    if not settings.platega_enabled:
        await callback.answer("Platega не настроена", show_alert=True)
        return
    data = await state.get_data()
    order_id = data.get("order_id") or str(uuid.uuid4())
    price_rub = float(data.get("price_rub") or 0)
    stars = int(data.get("stars") or 0)
    recipient = data.get("recipient", "")

    client = PlategaClient(settings)
    try:
        resp = await client.create_payment(
            CreatePaymentRequest(
                payment_method=2,
                amount=price_rub,
                currency="RUB",
                description=f"Stars x{stars} @{recipient}",
                return_url=settings.platega_return_url or "https://t.me/",
                failed_url=settings.platega_return_url or "https://t.me/",
                payload=order_id,
                metadata={"order_id": order_id, "stars": stars, "recipient": recipient},
            )
        )
    except Exception as exc:
        logger.exception("platega_create_failed", error=str(exc))
        await callback.answer(f"Ошибка Platega: {exc}", show_alert=True)
        return
    finally:
        await client.aclose()

    pay_url = resp.redirect or ""
    await state.update_data(
        pay_provider="platega",
        platega_tx_id=resp.transaction_id,
        pay_url=pay_url,
    )
    await state.set_state(BuyStars.awaiting_payment)
    text = t.STARS_PAYMENT_SBP.format(
        order_id=order_id[:8],
        stars=stars,
        username=recipient,
        price_rub=price_rub,
        ttl_min=settings.order_ttl_min,
    )
    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=stars_payment(pay_url, f"stars:check:platega:{resp.transaction_id}"),
        )
    await callback.answer()


@router.callback_query(F.data == "stars:pay:crypto")
async def pay_crypto(callback: CallbackQuery, state: FSMContext) -> None:
    settings = get_settings()
    if not settings.cryptobot_enabled:
        await callback.answer("CryptoBot не настроен", show_alert=True)
        return
    data = await state.get_data()
    order_id = data.get("order_id") or str(uuid.uuid4())
    price_ton = float(data.get("price_ton") or 0)
    stars = int(data.get("stars") or 0)
    recipient = data.get("recipient", "")

    amount_str = f"{price_ton:.4f}".rstrip("0").rstrip(".")
    client = CryptoBotClient(settings)
    try:
        inv = await client.create_invoice(
            amount=amount_str,
            asset=settings.cryptobot_asset,
            description=f"{stars} Stars → @{recipient}",
            payload=order_id,
            expires_in=settings.order_ttl_min * 60,
        )
    except Exception as exc:
        logger.exception("cryptobot_create_failed", error=str(exc))
        await callback.answer(f"Ошибка CryptoBot: {exc}", show_alert=True)
        return
    finally:
        await client.aclose()

    pay_url = inv.get("bot_invoice_url") or inv.get("pay_url") or inv.get("mini_app_invoice_url") or ""
    invoice_id = inv.get("invoice_id")
    await state.update_data(
        pay_provider="cryptobot",
        cryptobot_invoice_id=invoice_id,
        pay_url=pay_url,
    )
    await state.set_state(BuyStars.awaiting_payment)
    text = t.STARS_PAYMENT_CRYPTO.format(
        order_id=order_id[:8],
        stars=stars,
        username=recipient,
        amount=amount_str,
        asset=settings.cryptobot_asset,
        ttl_min=settings.order_ttl_min,
    )
    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=stars_payment(pay_url, f"stars:check:crypto:{invoice_id}"),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("stars:check:platega:"))
async def check_platega(callback: CallbackQuery, state: FSMContext) -> None:
    settings = get_settings()
    tx_id = (callback.data or "").split(":")[-1]
    client = PlategaClient(settings)
    try:
        status = await client.get_status(tx_id)
    except Exception as exc:
        await callback.answer(f"Ошибка проверки: {exc}", show_alert=True)
        return
    finally:
        await client.aclose()

    st = (status.status or "").upper()
    if st in {"CONFIRMED", "PAID", "SUCCESS", "COMPLETED"}:
        await _mark_paid_and_notify(callback, state, provider="platega")
    elif st in {"CANCELED", "CANCELLED", "FAILED"}:
        await callback.answer("Платёж отменён", show_alert=True)
    else:
        await callback.answer(f"Статус: {status.status}. Подождите и проверьте снова.")


@router.callback_query(F.data.startswith("stars:check:crypto:"))
async def check_crypto(callback: CallbackQuery, state: FSMContext) -> None:
    settings = get_settings()
    inv_id = (callback.data or "").split(":")[-1]
    try:
        invoice_id = int(inv_id)
    except ValueError:
        await callback.answer("Некорректный invoice id", show_alert=True)
        return
    client = CryptoBotClient(settings)
    try:
        items = await client.get_invoices(invoice_ids=[invoice_id])
    except Exception as exc:
        await callback.answer(f"Ошибка проверки: {exc}", show_alert=True)
        return
    finally:
        await client.aclose()

    if not items:
        await callback.answer("Инвойс не найден", show_alert=True)
        return
    inv = items[0]
    st = (inv.get("status") or "").lower()
    if st == "paid":
        await _mark_paid_and_notify(callback, state, provider="cryptobot")
    elif st in {"expired", "cancelled"}:
        await callback.answer("Счёт истёк или отменён", show_alert=True)
    else:
        await callback.answer(f"Статус: {st}. Оплатите и нажмите снова.")


async def _mark_paid_and_notify(
    callback: CallbackQuery, state: FSMContext, *, provider: str
) -> None:
    data = await state.get_data()
    stars = int(data.get("stars") or 0)
    recipient = str(data.get("recipient") or "")
    order_id = str(data.get("order_id") or "")
    await state.clear()
    text = (
        f"✅ <b>Оплата получена</b> ({provider})\n\n"
        f"⭐ {stars} → @{recipient}\n\n"
        f"⏳ Запускаем автовыдачу на Fragment…"
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=coming_soon_kb())

    settings = get_settings()
    bot = callback.bot
    uid = callback.from_user.id if callback.from_user else 0
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                f"💰 Оплата {provider}\n⭐ {stars} → @{recipient}\n"
                f"User: {uid}\norder={order_id}",
            )
        except Exception:
            pass

    # AUTO DELIVERY
    from app.services.fulfillment import schedule_fulfill

    schedule_fulfill(
        bot,
        user_id=uid,
        order_id=order_id or str(uid),
        username=recipient,
        stars=stars,
        chat_id=callback.message.chat.id if callback.message else uid,
    )
    await callback.answer("Оплата подтверждена! Выдаём Stars…")
