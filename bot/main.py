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
    try:
        logger.info("🚀 Бот запускается...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception:
        logger.exception("❌ Критическая ошибка при работе бота")