from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def day_keyboard(active: str) -> InlineKeyboardMarkup:
    today_text = "📅 Сегодня"
    tomorrow_text = "⏭ Завтра"

    if active == "today":
        today_text += " ✅"
    elif active == "tomorrow":
        tomorrow_text += " ✅"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=today_text,
                    callback_data="day:today",
                ),
                InlineKeyboardButton(
                    text=tomorrow_text,
                    callback_data="day:tomorrow",
                ),
            ]
        ]
    )
