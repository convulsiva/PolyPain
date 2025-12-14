# Подключение к БД, базовые функции
from tortoise import Tortoise


async def init_db() -> None:
    await Tortoise.init(
        db_url="sqlite://storage/db.sqlite3",
        modules={"models": ["bot.infra.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()
