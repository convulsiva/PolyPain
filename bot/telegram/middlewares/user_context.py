from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.infra.repositories.user import UserRepository


class UserContextMiddleware(BaseMiddleware):
    def __init__(self, users_repo: UserRepository) -> None:
        self.users_repo = users_repo

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = None
        chat_id = None

        if isinstance(event, Message):
            user = event.from_user
            chat_id = event.chat.id

        elif isinstance(event, CallbackQuery):
            user = event.from_user
            chat_id = event.message.chat.id if event.message else None

        if user and chat_id:
            await self.users_repo.get_or_create(
                chat_id=chat_id,
                username=user.username,
                first_name=user.first_name,
            )

            data["users_repo"] = self.users_repo

        return await handler(event, data)
