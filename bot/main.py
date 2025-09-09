from config import Config
from logging_conf import setup_logging
import logging
import telebot
import handlers

setup_logging()
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(Config.BOT_TOKEN)

handlers.register_handlers(bot)

if __name__ == "__main__":
    logger.info(" Бот запущен...")
    bot.infinity_polling()
