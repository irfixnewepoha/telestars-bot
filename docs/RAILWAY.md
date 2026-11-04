# Деплой на Railway — чеклист

1. Репозиторий на GitHub (приватный ок).
2. Railway → New Project → Deploy from GitHub.
3. Add plugin **PostgreSQL**, Add plugin **Redis**.
4. В сервисе приложения (не в БД) задать:

| Variable | Пример |
|----------|--------|
| `BOT_TOKEN` | от BotFather |
| `ADMIN_IDS` | `123456789` |
| `BRAND_NAME` | `MyStars` |
| `DATABASE_URL` | `postgresql+asyncpg://...` (из Postgres, схема asyncpg) |
| `REDIS_URL` | из Redis plugin |
| `USE_POLLING` | `true` |
| `ENVIRONMENT` | `production` |
| `SUPPORT_URL` | `https://t.me/...` |

5. Start Command (если переопределяете): `python -m app.main`
6. После деплоя: `/start` в боте.
7. Worker — второй сервис, Start: `python -m app.worker` (когда будет готов fulfillment).

Миграции вручную один раз (Railway shell или one-off):

```
alembic upgrade head
```

Либо добавьте в Dockerfile/CMD скрипт `alembic upgrade head && python -m app.main`.
