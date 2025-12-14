import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import Config
from bot.infra.db import close_db, init_db
from bot.infra.repositories.user import UserRepository
from bot.telegram.middlewares.user_context import UserContextMiddleware
from bot.telegram.routers.user.common import router as user_common


async def main() -> None:
    print("🚀 PolyPain bot starting...")

    # === init database ===
    await init_db()

    # === bot ===
    bot = Bot(
        token=Config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # === dispatcher ===
    dp = Dispatcher()

    # === repositories ===
    users_repo = UserRepository()

    # === middlewares ===
    dp.message.middleware(UserContextMiddleware(users_repo))

    # === routers ===
    dp.include_router(user_common)

    try:
        await dp.start_polling(bot)
    finally:
        # === graceful shutdown ===
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
