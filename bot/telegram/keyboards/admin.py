from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="📢 Рассылка")],
            [KeyboardButton(text="🧹 Очистить кэш")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        persistent=True,
    )
