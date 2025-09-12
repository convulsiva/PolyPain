from telebot import TeleBot
from telebot.types import Message
from datetime import datetime, timedelta
from keyboards import main_menu
from services.user_storage import add_user, update_user_group, load_users
from texts import START_MESSAGE, HELP_MESSAGE, INVALID_GROUP_FORMAT, GROUP_SAVED, NOT_REGISTERED, NO_GROUP, PING, DAYS_RU
import re

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        add_user(
            chat_id=message.chat.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        bot.send_message(message.chat.id, START_MESSAGE, reply_markup=main_menu())

    # TODAY
    def get_today_text():
        today_eng = datetime.now().strftime("%A")
        today = DAYS_RU.get(today_eng, today_eng)
        return f"📅 Сегодня {today}\n09:00 — Математика\n10:40 — Физика"

    @bot.message_handler(commands=["today"])
    def today_command(message: Message):
        bot.reply_to(message, get_today_text())

    @bot.message_handler(func=lambda msg: msg.text == "📅 Сегодня")
    def today_button(message: Message):
        bot.reply_to(message, get_today_text())

    # TOMORROW
    def get_tomorrow_text():
        tomorrow_eng = (datetime.now() + timedelta(days=1)).strftime("%A")
        tomorrow = DAYS_RU.get(tomorrow_eng, tomorrow_eng)
        return f"📅 Завтра {tomorrow}\n09:00 — Программирование\n10:40 — Английский"

    @bot.message_handler(commands=["tomorrow"])
    def tomorrow_command(message: Message):
        bot.reply_to(message, get_tomorrow_text())

    @bot.message_handler(func=lambda msg: msg.text == "📆 Завтра")
    def tomorrow_button(message: Message):
        bot.reply_to(message, get_tomorrow_text())

    # ===== SCHEDULE =====
    def get_schedule_text(group: str):
        return (
            f"📅 Расписание для группы {group}\n\n"
            "Понедельник:\n09:00 — Математика\n10:40 — Физика\n\n"
            "Вторник:\n09:00 — Программирование\n10:40 — Английский\n\n"
            "Среда:\n09:00 — Химия\n10:40 — История\n"
        )

    def handle_schedule(message: Message):
        users = load_users()
        chat_id = message.chat.id
        user = next((u for u in users["users"] if u["chat_id"] == chat_id), None)

        if not user:
            bot.reply_to(message, NOT_REGISTERED)
            return
        if not user.get("group"):
            bot.reply_to(message, NO_GROUP)
            return

        bot.reply_to(message, get_schedule_text(user["group"]))

    @bot.message_handler(commands=["schedule"])
    def schedule_command(message: Message):
        handle_schedule(message)

    @bot.message_handler(func=lambda msg: msg.text == "🗓 Всё расписание")
    def schedule_button(message: Message):
        handle_schedule(message)


    @bot.message_handler(commands=["ping"])
    def ping_handler(message: Message):
        bot.reply_to(message, PING)

    @bot.message_handler(commands=["id"])
    def id_handler(message: Message):
        bot.reply_to(message, f"🆔 Твой chat_id: {message.chat.id}")

    @bot.message_handler(commands=["help"])
    def help_handler(message: Message):
        bot.reply_to(message, HELP_MESSAGE)

    @bot.message_handler(commands=["setgroup"])
    def setgroup_handler(message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "❌ Использование: /setgroup <номер группы>")
            return

        group = parts[1].strip()

        if not re.fullmatch(r"\d+/\d+", group):
            bot.reply_to(message, INVALID_GROUP_FORMAT)
            return

        update_user_group(message.chat.id, group)
        bot.reply_to(message, GROUP_SAVED.format(group=group))


