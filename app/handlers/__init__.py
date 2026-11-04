from __future__ import annotations

from aiogram import Dispatcher

from app.handlers import about, admin, errors, profile, start, stars


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(errors.router)
    dp.include_router(start.router)
    dp.include_router(stars.router)
    dp.include_router(profile.router)
    dp.include_router(about.router)
    dp.include_router(admin.router)
