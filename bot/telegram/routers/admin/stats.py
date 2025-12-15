from aiogram import F, Router
from aiogram.types import Message

from bot.infra.repositories.user import UserRepository
from bot.telegram.filters.is_admin import IsAdmin

router = Router()
router.message.filter(IsAdmin())


@router.message(F.text == "📊 Статистика")
async def admin_stats(message: Message, users_repo: UserRepository) -> None:
    total = await users_repo.count_all()
    with_group = await users_repo.count_with_group()

    await message.answer(
        "📊 <b>Статистика</b>\n\n"
        f"👤 Пользователей всего: <b>{total}</b>\n"
        f"🎓 С группой: <b>{with_group}</b>"
    )
