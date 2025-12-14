from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.infra.repositories.user import UserRepository

router = Router()
users_repo = UserRepository()


@router.message(CommandStart())
async def start(message: Message):
    await users_repo.get_or_create(
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    await message.answer("✅ PolyPain bot запущен\nТы сохранён в базе 👌")


@router.message(Command("ping"))
async def ping(message: Message):
    await message.answer("🏓 pong")
