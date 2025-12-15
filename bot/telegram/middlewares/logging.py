import logging

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

logger = logging.getLogger("bot.events")


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            logger.info(
                "MESSAGE | user=%s chat=%s text=%r",
                event.from_user.id,
                event.chat.id,
                event.text,
            )

        elif isinstance(event, CallbackQuery):
            logger.info(
                "CALLBACK | user=%s data=%r",
                event.from_user.id,
                event.data,
            )

        return await handler(event, data)
