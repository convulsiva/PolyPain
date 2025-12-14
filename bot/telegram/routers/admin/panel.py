from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.telegram.filters.is_admin import IsAdmin
from bot.telegram.keyboards.admin import admin_keyboard
from bot.telegram.keyboards.main_menu import main_menu_keyboard

router = Router()
router.message.filter(IsAdmin())


@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    await message.answer(
        "🛠 <b>Админ-панель</b>\n\nВыбери действие:",
        reply_markup=admin_keyboard(),
    )


# ⬅️ Назад — ВЫХОД ИЗ АДМИНКИ
@router.message(F.text == "⬅️ Назад")
async def admin_back(message: Message) -> None:
    await message.answer(
        "↩️ Возврат в главное меню",
        reply_markup=main_menu_keyboard(),
    )
