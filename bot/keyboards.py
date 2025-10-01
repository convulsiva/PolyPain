from telebot.types import ReplyKeyboardMarkup, KeyboardButton

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
