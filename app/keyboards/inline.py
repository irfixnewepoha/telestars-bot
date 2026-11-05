from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import get_settings
from app.texts import ru as t

QUICK_AMOUNTS = (50, 100, 250, 500, 1000, 2500)


def _home_btn() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=t.HOME, callback_data="menu:home")


def main_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="⭐ Stars", callback_data="menu:stars"),
        InlineKeyboardButton(text="👑 Premium", callback_data="menu:premium"),
    )
    b.row(
        InlineKeyboardButton(text="🎁 Подарки", callback_data="menu:gifts"),
        InlineKeyboardButton(text="💎 GRAM", callback_data="menu:gram"),
    )
    b.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="menu:profile"),
        InlineKeyboardButton(text="ℹ️ О сервисе", callback_data="menu:about"),
    )
    return b.as_markup()


def stars_section() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⭐ Купить Stars", callback_data="stars:buy"))
    b.row(InlineKeyboardButton(text="💸 Продать Stars", callback_data="stars:sell"))
    b.row(_home_btn())
    return b.as_markup()


def stars_recipient() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="👤 Купить себе", callback_data="stars:self"))
    b.row(InlineKeyboardButton(text=t.BACK, callback_data="menu:stars"))
    b.row(_home_btn())
    return b.as_markup()


def stars_amount_nav() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    row: list[InlineKeyboardButton] = []
    for i, n in enumerate(QUICK_AMOUNTS):
        row.append(InlineKeyboardButton(text=f"{n} ⭐", callback_data=f"stars:qty:{n}"))
        if len(row) == 3:
            b.row(*row)
            row = []
    if row:
        b.row(*row)
    b.row(InlineKeyboardButton(text=t.BACK, callback_data="stars:back_recipient"))
    b.row(_home_btn())
    return b.as_markup()


def stars_confirm(can_sbp: bool, can_crypto: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if can_crypto:
        b.row(
            InlineKeyboardButton(
                text="💎 Оплатить TON (CryptoBot)",
                callback_data="stars:pay:crypto",
            )
        )
    if can_sbp:
        b.row(
            InlineKeyboardButton(
                text="💳 Оплатить СБП",
                callback_data="stars:pay:sbp",
            )
        )
    if not can_sbp and not can_crypto:
        b.row(
            InlineKeyboardButton(
                text="⚠️ Оплата временно недоступна",
                callback_data="stars:pay:none",
            )
        )
    b.row(InlineKeyboardButton(text=t.BACK, callback_data="stars:back_amount"))
    b.row(_home_btn())
    return b.as_markup()


def stars_payment(pay_url: str, check_data: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💳 Перейти к оплате", url=pay_url))
    b.row(InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=check_data))
    b.row(_home_btn())
    return b.as_markup()


def profile_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t.HISTORY, callback_data="profile:history:0"))
    b.row(
        InlineKeyboardButton(text=t.REFERRAL, callback_data="profile:referral"),
        InlineKeyboardButton(text=t.PROMO, callback_data="profile:promo"),
    )
    b.row(_home_btn())
    return b.as_markup()


def about_kb() -> InlineKeyboardMarkup:
    settings = get_settings()
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t.FAQ, callback_data="about:faq"))
    if settings.support_url:
        b.row(InlineKeyboardButton(text=t.SUPPORT, url=settings.support_url))
    else:
        b.row(InlineKeyboardButton(text=t.SUPPORT, callback_data="about:support"))
    if settings.privacy_url:
        b.row(InlineKeyboardButton(text=t.PRIVACY, url=settings.privacy_url))
    if settings.terms_url:
        b.row(InlineKeyboardButton(text=t.TERMS, url=settings.terms_url))
    if settings.offer_url:
        b.row(InlineKeyboardButton(text=t.OFFER, url=settings.offer_url))
    b.row(_home_btn())
    return b.as_markup()


def home_only() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(_home_btn())
    return b.as_markup()


def coming_soon_kb() -> InlineKeyboardMarkup:
    return home_only()
