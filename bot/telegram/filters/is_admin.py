from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.infra.repositories.admin import AdminRepository


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        repo = AdminRepository()
        return await repo.is_admin(message.from_user.id)
