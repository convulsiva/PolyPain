from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

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
        if isinstance(event, Message) and event.from_user:
            await self.users_repo.get_or_create(
                chat_id=event.chat.id,
                username=event.from_user.username,
                first_name=event.from_user.first_name,
            )

            # прокидываем репозиторий в handlers
            data["users_repo"] = self.users_repo

        return await handler(event, data)
