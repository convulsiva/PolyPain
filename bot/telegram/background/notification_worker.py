import asyncio
import logging

from bot.config import config
from bot.services.notifications import NotificationService

logger = logging.getLogger(__name__)


async def start_notification_worker(bot, users_repo) -> None:
    service = NotificationService()
    minutes = config.NOTIFY_BEFORE_MINUTES

    logger.info("Notification worker started (%s min before)", minutes)

    while True:
        try:
            await service.check_and_notify(
                bot=bot,
                users_repo=users_repo,
                minutes_before=minutes,
            )
        except Exception:
            logger.exception("Notification worker error")

        await asyncio.sleep(60)
