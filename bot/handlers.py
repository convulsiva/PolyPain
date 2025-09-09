from telebot import TeleBot
from telebot.types import Message
from services.user_storage import add_user, update_user_group

def register_handlers(bot):
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        add_user(message.chat.id, message.from_user.username, message.from_user.first_name)
        bot.reply_to(message, "Привет! Ты добавлен в базу ✅")

    @bot.message_handler(commands=["ping"])
    def ping_handler(message: Message):
        bot.reply_to(message, "pong 🏓")

    @bot.message_handler(commands=["help"])
    def help_handler(message: Message):
        bot.reply_to(message, (
            "📖 Доступные команды:\n"
            "/start - приветствие и добавление в базу\n"
            "/ping - проверить, жив ли бот\n"
            "/help - список команд\n"
            "/setgroup <номер> - сохранить свою группу\n"
            "/schedule - показать расписание (если указана группа)\n"
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