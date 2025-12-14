import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import config
from bot.infra.db import close_db, init_db
from bot.infra.repositories.admin import AdminRepository
from bot.infra.repositories.user import UserRepository
from bot.telegram.middlewares.logging import LoggingMiddleware
from bot.telegram.middlewares.user_context import UserContextMiddleware
from bot.telegram.routers.admin.broadcast import router as admin_broadcast
from bot.telegram.routers.admin.manage_admins import router as admin_manage
from bot.telegram.routers.admin.panel import router as admin_panel
from bot.telegram.routers.admin.stats import router as admin_stats
from bot.telegram.routers.user.common import router as user_common
from bot.utils.logging_conf import setup_logging

# --- logging ---
setup_logging()
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("🚀 PolyPain bot starting...")

    # --- init db ---
    await init_db()

    # --- bootstrap admins from .env ---
    admin_repo = AdminRepository()
    for admin_id in config.ADMIN_IDS:
        await admin_repo.add_admin(admin_id)

    # --- bot ---
    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set in environment")

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # --- dispatcher ---
    dp = Dispatcher()

    # --- repositories ---
    users_repo = UserRepository()

    # --- middlewares ---
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(UserContextMiddleware(users_repo))
    dp.callback_query.middleware(UserContextMiddleware(users_repo))

    # --- routers ---
    dp.include_router(user_common)

    dp.include_router(admin_panel)
    dp.include_router(admin_stats)
    dp.include_router(admin_broadcast)
    dp.include_router(admin_manage)

    try:
        await dp.start_polling(bot)
    except Exception:
        logger.exception("🔥 Unhandled exception in polling")
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
