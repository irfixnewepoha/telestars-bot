from __future__ import annotations

from app.config import get_settings


def brand() -> str:
    return get_settings().brand_name


# --- Главный экран (как у PSINA) ---
WELCOME = (
    "👋 Добро пожаловать в <b>{brand}</b>!\n\n"
    "Выберите нужный раздел"
)

TECH_CHANNEL_HINT = "Технический канал"

# --- Stars ---
STARS_SECTION = (
    "⭐ <b>Telegram Stars</b>\n\n"
    "Выберите нужный раздел"
)

STARS_CHOOSE_RECIPIENT = (
    "⭐ <b>Telegram Stars</b>\n\n"
    "👇 Выберите, кому отправим Stars:\n\n"
    "<blockquote>"
    "— Если хотите купить себе, выберите «Себе»\n"
    "— Если хотите подарить другому, просто введите юзернейм"
    "</blockquote>\n\n"
    "🔍 Пример: @username"
)

STARS_ENTER_AMOUNT = (
    "⭐ <b>Telegram Stars</b>\n\n"
    "<blockquote>👤 Получатель: @{username}</blockquote>\n\n"
    "✅ Введите количество звёзд для покупки (от {min_stars} до {max_stars})."
)

STARS_CONFIRM = (
    "⭐ <b>Подтверждение заказа</b>\n\n"
    "Получатель: <b>@{username}</b>{name_part}\n"
    "Количество: <b>{stars}</b> ⭐\n"
    "К оплате: <b>{price_rub:.2f} ₽</b>\n\n"
    "⚠️ Звёзды зачисляются без возможности отмены."
)

STARS_PAYMENT = (
    "💳 <b>Оплата</b>\n\n"
    "Заказ: <code>{order_id}</code>\n"
    "К оплате: <b>{price_rub:.2f} ₽</b>\n"
    "Срок: {ttl_min} мин.\n\n"
    "Нажмите «Оплатить», затем «Проверить оплату»."
)

STARS_PAID = "⏳ Оплата получена, зачисляем звёзды…"
STARS_COMPLETED = "✅ Готово: <b>{stars}</b> ⭐ отправлено @{username}"
STARS_FAILED = "❌ Не удалось выдать звёзды. Средства возвращены на внутренний баланс."

# --- Профиль (как у PSINA) ---
PROFILE = (
    "👤 <b>Профиль</b>\n\n"
    "🪪 ID: <code>{user_id}</code>\n"
    "📛 Имя: @{username}\n\n"
    "🦴 Баланс: <b>{balance_rub:.2f} ₽</b>\n\n"
    "<blockquote>"
    "📁 Заказы:\n"
    "👑 Куплено Premium: {premium_months} мес.\n"
    "⭐ Куплено Stars: {stars_bought} шт.\n"
    "💎 Куплено GRAM(TON): {gram_bought} шт.\n"
    "🎁 Куплено подарков: {gifts_bought} шт.\n"
    "💸 Продано Stars: {stars_sold} шт.\n"
    "Всего потрачено: {spent_rub:.2f} ₽"
    "</blockquote>\n\n"
    "👇 Выберите действие:"
)

# --- О сервисе ---
ABOUT = (
    "ℹ️ <b>О сервисе</b>\n\n"
    "Выберите интересующий раздел:"
)

# --- Скоро / заглушки ---
COMING_SOON_SECTION = (
    "🚧 <b>{title}</b>\n\n"
    "Раздел скоро будет доступен.\n"
    "Сейчас работаем только с покупкой Stars."
)

PREMIUM_STUB = COMING_SOON_SECTION.format(title="Telegram Premium")
GIFTS_STUB = COMING_SOON_SECTION.format(title="Подарки")
GRAM_STUB = (
    "💎 <b>GRAM (TON)</b>\n\n"
    "Раздел в разработке. Следите за обновлениями."
)
SELL_STUB = "💸 Продажа Stars скоро будет доступна."
REFERRAL_STUB = "Реферальная система — скоро."
PROMO_STUB = "Промокоды — скоро."
LANG_STUB = "Смена языка — скоро."

# --- Общее ---
MAINTENANCE = "Сервис временно недоступен. Попробуйте позже."
BANNED = "Доступ ограничен."
OLD_MESSAGE = "Сообщение устарело. Вернитесь в главное меню."
INVALID_USERNAME = "Некорректный username. Формат: @username (5–32 символа, латиница/цифры/_)."
RECIPIENT_NOT_FOUND = "Получатель @{username} не найден. Проверьте username и попробуйте снова."
INVALID_AMOUNT = "Введите целое число от {min_stars} до {max_stars}."

BACK = "⬅️ Назад"
HOME = "🏠 Главное меню"
BUY_SELF = "👤 Купить себе"
BUY = "⭐ Купить"
SELL = "💸 Продать"
PAY_SBP = "Оплатить СБП"
CHECK_PAYMENT = "Проверить оплату"
PAY_BALANCE = "Оплатить с баланса"
HISTORY = "🧾 История заказов"
COMING_SOON = "Скоро"
FAQ = "❓ FAQ"
PRIVACY = "🔒 Политика конфиденциальности"
TERMS = "📄 Пользовательское соглашение"
OFFER = "📢 Публичная оферта"
SUPPORT = "💬 Контакты поддержки"
REFERRAL = "👥 Реферальная система"
PROMO = "🎁 Промокоды"
CHANGE_LANG = "🌐 Сменить язык"
