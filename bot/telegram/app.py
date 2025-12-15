from aiogram import Dispatcher

from bot.telegram.routers.admin.panel import router as admin_panel_router
from bot.telegram.routers.admin.stats import router as admin_stats_router
from bot.telegram.routers.user.common import router as user_router


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(user_router)
    dp.include_router(admin_panel_router)  # 👈 ОБЯЗАТЕЛЬНО
    dp.include_router(admin_stats_router)  # 👈 ОБЯЗАТЕЛЬНО
