import telebot
from config import Config
import handlers

bot = telebot.TeleBot(Config.BOT_TOKEN, parse_mode="HTML")

handlers.register_handlers(bot)

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()