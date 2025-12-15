from pathlib import Path

from tortoise import Tortoise

BASE_DIR = Path(__file__).resolve().parent.parent  # bot/
DB_DIR = BASE_DIR / "storage"
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "database.db"


async def init_db() -> None:
    await Tortoise.init(
        db_url=f"sqlite://{DB_PATH.resolve()}",
        modules={"models": ["bot.infra.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()
