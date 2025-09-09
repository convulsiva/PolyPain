from telebot.types import Message
from services.user_storage import add_user

def register_handlers(bot):
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        add_user(message.chat.id, message.from_user.username, message.from_user.first_name)
        bot.reply_to(message, "Привет! Ты добавлен в базу ✅")

    @bot.message_handler(commands=["ping"])
    def ping_handler(message: Message):
        bot.reply_to(message, "pong 🏓")