from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def week_keyboard(offset: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Предыдущая",
                    callback_data=f"week:{offset - 1}",
                ),
                InlineKeyboardButton(
                    text="🔄 Текущая",
                    callback_data="week:0",
                ),
                InlineKeyboardButton(
                    text="➡️ Следующая",
                    callback_data=f"week:{offset + 1}",
                ),
            ]
        ]
    )
