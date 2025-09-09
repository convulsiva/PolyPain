from telebot import TeleBot
from telebot.types import Message

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        bot.reply_to(message, "Привет! Я твой бот ")

    @bot.message_handler(commands=["ping"])
    def ping_handler(message: Message):
        bot.reply_to(message, "pong")
