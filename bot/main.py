import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import config
from bot.infra.db import close_db, init_db
from bot.infra.repositories.user import UserRepository
from bot.telegram.middlewares.user_context import UserContextMiddleware
from bot.telegram.routers.user.common import router as user_common


async def main() -> None:
    print("🚀 PolyPain bot starting...")

    # --- init db ---
    await init_db()

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
    user_middleware = UserContextMiddleware(users_repo)

    dp.message.middleware(user_middleware)
    dp.callback_query.middleware(user_middleware)

    # --- routers ---
    dp.include_router(user_common)

    try:
        await dp.start_polling(bot)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
