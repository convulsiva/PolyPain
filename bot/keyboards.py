from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton("📅 Сегодня"),
        KeyboardButton("📆 Завтра")
    )
    markup.row(
        KeyboardButton("🗓 Всё расписание")
    )
    return markup


def build_admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Статистика", callback_data="admin:stats"),
        InlineKeyboardButton("✉️ Написать пользователю", callback_data="admin:dm"),
    )
    kb.add(
        InlineKeyboardButton("👥 Админы", callback_data="admin:list"),
    )
    return kb
