# Деплой на Railway — полная инструкция

## 0. Что уже умеет бот после деплоя

- Меню как у PSINA (Stars / Premium «скоро» / …)
- Покупка Stars: себе или @username → сумма → **СБП (Platega)** и/или **TON (CryptoBot)**
- Проверка оплаты кнопкой
- Уведомление админам об успешной оплате
- Автовыдача Stars на Fragment — **отдельный этап** (нужен worker + RealFragmentClient / сторонний Fragment API). Пока после оплаты админ видит заказ и может выдать вручную.

## 1. Создать бота Telegram

1. @BotFather → `/newbot` → скопировать **BOT_TOKEN**
2. @userinfobot → ваш **ADMIN_IDS** (число)

## 2. Platega (СБП), опционально но желательно

1. Регистрация: https://app.platega.io  
2. Настройки → **MerchantId** и **X-Secret**  
3. В env: `PLATEGA_MERCHANT_ID`, `PLATEGA_SECRET`  
4. Callback URL (когда будет публичный URL Railway):  
   `https://ВАШ-ДОМЕН.up.railway.app` + `PLATEGA_WEBHOOK_PATH`  
   Пока `USE_POLLING=true` — проверка оплаты идёт кнопкой «Проверить оплату» через API статуса.

## 3. CryptoBot (TON)

1. Откройте [@CryptoBot](https://t.me/CryptoBot) (mainnet) или [@CryptoTestnetBot](https://t.me/CryptoTestnetBot)  
2. **Crypto Pay** → **Create App** → скопировать **API Token**  
3. В env: `CRYPTOBOT_TOKEN=...`  
4. `CRYPTOBOT_TESTNET=false` для боевого  

Документация: https://help.crypt.bot/crypto-pay-api  

## 4. TON на выдачу Stars

Положите **≥ 1.5 TON** (лучше больше) на кошелёк, с которого будете покупать на Fragment.  
Автовыдача в этом релизе уведомляет админа; worker/Fragment — следующий шаг (см. `docs/FIRST_RUN.md`).

Важно (как в похожих проектах): свежий кошелёк лучше один раз вручную провести покупку на Fragment, V4R2 часто стабильнее.

## 5. Railway по шагам

1. Залейте код на GitHub (приватный репозиторий).  
2. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**.  
3. **Add Plugin** → PostgreSQL.  
4. **Add Plugin** → Redis (рекомендуется).  
5. В сервисе приложения → **Variables**:

```
BOT_TOKEN=...
ADMIN_IDS=ваш_id
BRAND_NAME=MyStars
USE_POLLING=true
ENVIRONMENT=production
STAR_PRICE_RUB=1.5
STAR_PRICE_TON=0.013

# хотя бы один способ оплаты:
PLATEGA_MERCHANT_ID=...
PLATEGA_SECRET=...
CRYPTOBOT_TOKEN=...
CRYPTOBOT_TESTNET=false

DATABASE_URL=postgresql+asyncpg://...   # из Postgres, схема asyncpg!
REDIS_URL=...                           # из Redis plugin
SUPPORT_URL=https://t.me/...
```

6. **Settings → Deploy**: Dockerfile подхватится сам (`railway.toml`).  
7. Дождитесь Deploy Success → напишите боту `/start`.

### DATABASE_URL

Railway часто даёт `postgres://user:pass@host:port/db`.  
Нужно: `postgresql+asyncpg://user:pass@host:port/db`.

### Миграции (один раз)

Railway → сервис → **Shell** или one-off:

```bash
alembic upgrade head
```

Или временно в Dockerfile CMD:  
`alembic upgrade head && python -m app.main`

## 6. Проверка оплаты

1. `/start` → Stars → Купить → себе → 50  
2. Оплатить СБП или TON  
3. «Проверить оплату»  
4. Админу должно прийти сообщение об оплате  

## 7. Что взять из dobrozor/tg_buy_stars

Похожий open-source бот использует ЮKassa + fragment-api.com + мнемонику.  
У нас: **Platega (СБП)** + **CryptoBot (TON)** + изолированный Fragment-клиент (mock/real).  
Их замечание про **первый ручной платёж с кошелька на Fragment** и **V4R2** — полезно и для нас.

## 8. Безопасность

- Не коммитьте `.env`  
- Не присылайте мнемонику в чаты  
- Отдельный TON-кошелёк только под бота  
