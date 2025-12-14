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
        ],
        resize_keyboard=True,
        persistent=True,
    )
