from aiogram import F, Router
from aiogram.types import Message

from bot.services.schedule import schedule_service
from bot.telegram.filters.is_admin import IsAdmin

router = Router()
router.message.filter(IsAdmin())


@router.message(F.text == "🧹 Очистить кэш")
async def clear_cache(message: Message) -> None:
    schedule_service.clear_all_cache()
    await message.answer("🧹 Кэш расписания очищен")
