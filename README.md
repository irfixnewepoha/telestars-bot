# Telegram Stars Bot — автовыдача

Покупатель платит (СБП / TON) → бот **сам** покупает Stars на Fragment с вашего TON-кошелька.

## Читать сначала

**[docs/ENV_ПРОСТЫМИ_СЛОВАМИ.md](docs/ENV_ПРОСТЫМИ_СЛОВАМИ.md)** — откуда каждая переменная.  
**[docs/DEPLOY_RAILWAY.md](docs/DEPLOY_RAILWAY.md)** — деплой на Railway.

## Что нужно минимум

1. `BOT_TOKEN` + `ADMIN_IDS`
2. `CRYPTOBOT_TOKEN` **или** Platega
3. `TON_MNEMONIC` — сид кошелька с TON (вы его пополняете)
4. Запас TON на этом кошельке

## Локально

```bash
cp .env.example .env
# заполнить
pip install -r requirements.txt
python -m app.main
```

## Важно

- Сид только в env Railway, никому не отправлять.
- Один раз вручную купите 50 Stars с этого кошелька на fragment.com.
- Рекомендуется кошелёк **V4R2**.
