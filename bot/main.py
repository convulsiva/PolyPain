import logging
import telebot
from bot.config import Config
from bot.logging_conf import setup_logging
from services.fan_worker import start_fan_worker
from bot import handlers
from bot.admin_panel import register_admin_handlers

setup_logging()
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(Config.BOT_TOKEN)

register_admin_handlers(bot)
handlers.register_handlers(bot)

start_fan_worker(bot)

if __name__ == "__main__":
    try:
        logger.info("🚀 Бот запускается...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception:
        logger.exception("❌ Критическая ошибка при работе бота")
