from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.infra.repositories.admin import AdminRepository
from bot.telegram.filters.is_admin import IsAdmin

router = Router()
router.message.filter(IsAdmin())

admin_repo = AdminRepository()


# 📋 список админов
@router.message(Command("admins"))
async def list_admins(message: Message) -> None:
    admins = await admin_repo.get_all_admins()

    if not admins:
        await message.answer("👀 Администраторы не найдены")
        return

    text = "🛠 <b>Администраторы</b>\n\n"
    for admin in admins:
        text += f"• <code>{admin.id}</code>\n"

    await message.answer(text)


# ➕ добавить админа
@router.message(Command("addadmin"))
async def add_admin(message: Message) -> None:
    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("❌ Используй:\n<code>/addadmin 123456789</code>")
        return

    user_id = int(parts[1])

    await admin_repo.add_admin(
        user_id=user_id,
        username=message.from_user.username,
    )

    await message.answer(f"✅ Пользователь <code>{user_id}</code> добавлен в админы")


# ❌ удалить админа
@router.message(Command("deladmin"))
async def remove_admin(message: Message) -> None:
    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("❌ Используй:\n<code>/deladmin 123456789</code>")
        return

    user_id = int(parts[1])

    if user_id == message.from_user.id:
        await message.answer("❌ Нельзя удалить самого себя")
        return

    await admin_repo.remove_admin(user_id)

    await message.answer(f"🗑 Администратор <code>{user_id}</code> удалён")
