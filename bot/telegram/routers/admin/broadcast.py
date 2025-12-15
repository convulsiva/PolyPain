from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.infra.repositories.user import UserRepository
from bot.telegram.filters.is_admin import IsAdmin
from bot.telegram.states.admin import BroadcastState

router = Router()
router.message.filter(IsAdmin())


# Шаг 1 — нажали кнопку
@router.message(F.text == "📢 Рассылка")
async def broadcast_start(message: Message, state: FSMContext) -> None:
    await state.set_state(BroadcastState.waiting_for_text)
    await message.answer(
        "📢 <b>Рассылка</b>\n\n"
        "Отправь текст, который нужно разослать всем пользователям.\n\n"
        "❌ Напиши <code>отмена</code> для выхода."
    )


# Шаг 2 — получили текст
@router.message(BroadcastState.waiting_for_text)
async def broadcast_send(
    message: Message,
    state: FSMContext,
    users_repo: UserRepository,
) -> None:
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("❌ Рассылка отменена")
        return

    users = await users_repo.get_all_chat_ids()

    sent = 0
    failed = 0

    for chat_id in users:
        try:
            text = (
                "📢 <b>Сообщение от администратора</b>\n"
                f"<i>{datetime.now():%d.%m.%Y %H:%M}</i>\n\n"
                f"{message.text}"
            )
            await message.bot.send_message(chat_id, text)
            sent += 1
        except Exception:
            failed += 1

    await state.clear()

    await message.answer(
        f"✅ <b>Рассылка завершена</b>\n\n📨 Отправлено: <b>{sent}</b>\n⚠️ Ошибок: <b>{failed}</b>"
    )
