from __future__ import annotations

from aiogram import Router
from aiogram.types import ErrorEvent

from app.utils.logging import get_logger

router = Router(name="errors")
logger = get_logger(__name__)


@router.error()
async def global_error_handler(event: ErrorEvent) -> bool:
    logger.exception("unhandled_error", error=str(event.exception))
    # Return True to mark as handled
    return True
