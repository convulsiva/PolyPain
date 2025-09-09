from telebot import TeleBot
from telebot.types import Message
from datetime import datetime, timedelta
from services.user_storage import add_user, update_user_group, load_users

def register_handlers(bot):
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        add_user(
            chat_id=message.chat.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        bot.reply_to(message, (
            "👋 Привет! Я бот для расписания занятий Политеха.\n\n"
            "Я могу:\n"
            "📅 Показывать расписание твоей группы\n"
            "✅ Сохранять группу, чтобы не вводить её каждый раз\n"
            "ℹ️ Подсказать список команд\n\n"
            "👉 Для начала укажи свою группу командой:\n"
            "/setgroup <номер группы>\n"
            "(например: /setgroup 3530901/00001)\n\n"
            "Напиши /help, чтобы узнать все команды."
        ))

    @bot.message_handler(commands=["ping"])
    def ping_handler(message: Message):
        bot.reply_to(message, "pong 🏓")

    @bot.message_handler(commands=["help"])
    def help_handler(message: Message):
        bot.reply_to(message, (
            "📖 Доступные команды:\n"
            "/start - приветствие и добавление в базу\n"
            "/ping - проверить, жив ли бот\n"
            "/setgroup <номер> - сохранить свою группу\n"
            "/schedule - показать расписание\n"
            "/today - расписание на сегодня\n"
            "/tomorrow - расписание на завтра\n"
        ))

    @bot.message_handler(commands=["setgroup"])
    def setgroup_handler(message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "❌ Использование: /setgroup <номер группы>")
            return

        group = parts[1].strip()
        update_user_group(message.chat.id, group)
        bot.reply_to(message, f"✅ Группа сохранена: {group}")

    @bot.message_handler(commands=["schedule"])
    def schedule_handler(message: Message):
        users = load_users()
        chat_id = message.chat.id

        user = next((u for u in users["users"] if u["chat_id"] == chat_id), None)

        if not user:
            bot.reply_to(message, "❌ Ты ещё не зарегистрирован. Напиши /start.")
            return

        if not user.get("group"):
            bot.reply_to(message, "❌ У тебя не сохранена группа. Введи /setgroup <номер группы>.")
            return

        group = user["group"]

        # заглушка расписания (потом на парсер)
        schedule_text = (
            f"📅 Расписание для группы {group}\n\n"
            "09:00 — Математика\n"
            "10:40 — Физика\n"
            "12:30 — Программирование\n"
        )

        bot.reply_to(message, schedule_text)

    @bot.message_handler(commands=["today"])
    def today_handler(message: Message):
        today = datetime.now().strftime("%A")
        bot.reply_to(message, f"📅 Сегодня {today}\n09:00 — Математика\n10:40 — Физика")

    @bot.message_handler(commands=["tomorrow"])
    def tomorrow_handler(message: Message):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A")
        bot.reply_to(message, f"📅 Завтра {tomorrow}\n09:00 — Программирование\n10:40 — Английский")