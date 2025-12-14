from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📅 Сегодня"),
                KeyboardButton(text="⏭ Завтра"),
            ],
            [
                KeyboardButton(text="📆 Неделя"),
            ],
            [KeyboardButton(text="🔔 Уведомления")],
        ],
        resize_keyboard=True,
        persistent=True,
    )
