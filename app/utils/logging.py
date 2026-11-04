from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from app.config import get_settings


def _mask_secrets(_: Any, __: Any, event_dict: dict[str, Any]) -> dict[str, Any]:
    sensitive_keys = {
        "token",
        "secret",
        "mnemonic",
        "cookies",
        "password",
        "api_key",
        "seed",
        "private_key",
    }
    for key in list(event_dict.keys()):
        lower = key.lower()
        if any(s in lower for s in sensitive_keys):
            event_dict[key] = "***MASKED***"
    return event_dict


def setup_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # PrintLogger has no .name — do NOT use structlog.stdlib.add_logger_name
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        _mask_secrets,
    ]

    if settings.environment == "development":
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=False),
        ]
    else:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=False,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)


def get_logger(name: str | None = None) -> Any:
    return structlog.get_logger(name)
