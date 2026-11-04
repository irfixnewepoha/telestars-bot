from __future__ import annotations

"""
Order fulfillment worker.

Uses SELECT ... FOR UPDATE SKIP LOCKED on orders table.
Processes paid → fulfilling → completed (or refund / manual_review).
"""

import asyncio

from app.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


async def process_once() -> int:
    """Claim and process one batch of paid orders. Returns number processed."""
    # TODO: implement with MockFragmentClient first
    return 0


async def main() -> None:
    setup_logging()
    logger.info("worker_started")
    while True:
        try:
            n = await process_once()
            if n == 0:
                await asyncio.sleep(2)
        except Exception:
            logger.exception("worker_loop_error")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
