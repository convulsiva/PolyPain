from aiogram import F, Router
from aiogram.types import Message

from bot.telegram.filters.is_admin import IsAdmin

router = Router()
router.message.filter(IsAdmin())


@router.message(F.text == "📢 Рассылка")
async def broadcast_stub(message: Message) -> None:
    await message.answer("📢 <b>Рассылка</b>\n\nФункция будет добавлена далее 👌")
