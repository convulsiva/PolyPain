import telebot
from config import Config
import handlers

bot = telebot.TeleBot(Config.BOT_TOKEN)

handlers.register_handlers(bot)

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()