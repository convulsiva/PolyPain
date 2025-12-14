from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.infra.repositories.user import UserRepository
from bot.services.schedule import ScheduleService
from bot.utils.schedule_formatter import format_day
from parsers.features.schedule.exceptions import (
    DayNotFoundError,
    GroupNotFoundError,
)

router = Router()
schedule_service = ScheduleService()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "👋 <b>PolyPain</b>\n\n"
        "Я показываю расписание Политеха 📅\n\n"
        "Команды:\n"
        "/setgroup — задать группу\n"
        "/today — расписание на сегодня\n"
        "/tomorrow — расписание на завтра"
    )


@router.message(Command("setgroup"))
async def set_group(message: Message, users_repo: UserRepository) -> None:
    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:
        await message.answer("❌ Укажи группу.\n\n<code>/setgroup 5130902/40003</code>")
        return

    group = parts[1].strip()

    if len(group) < 5 or " " in group:
        await message.answer("❌ Некорректный формат группы.")
        return

    await users_repo.set_group(message.chat.id, group)
    await message.answer(f"✅ Группа сохранена: <b>{group}</b>")


@router.message(Command("today"))
async def today(message: Message, users_repo: UserRepository) -> None:
    group = await users_repo.get_group(message.chat.id)

    if not group:
        await message.answer("❌ Группа не указана.\n\n<code>/setgroup 5130902/40003</code>")
        return

    try:
        day = schedule_service.get_today(group)
        await message.answer(format_day(day))

    except GroupNotFoundError:
        await message.answer("❌ Группа не найдена.")

    except DayNotFoundError:
        await message.answer("🎉 <b>Сегодня пар нет</b>")

    except Exception as e:
        # универсальная обработка "день не найден"
        if "Could not find day" in str(e):
            await message.answer("🎉 <b>Сегодня пар нет</b>")
        else:
            await message.answer("⚠️ Не удалось получить расписание. Попробуй позже.")


@router.message(Command("tomorrow"))
async def tomorrow(message: Message, users_repo: UserRepository) -> None:
    group = await users_repo.get_group(message.chat.id)

    if not group:
        await message.answer("❌ Группа не указана.\n\n<code>/setgroup 5130902/40003</code>")
        return

    try:
        day = schedule_service.get_tomorrow(group)
        await message.answer(format_day(day))

    except GroupNotFoundError:
        await message.answer("❌ Группа не найдена.")

    except DayNotFoundError:
        await message.answer("🎉 <b>Завтра пар нет</b>")

    except Exception as e:
        if "Could not find day" in str(e):
            await message.answer("🎉 <b>Завтра пар нет</b>")
        else:
            await message.answer("⚠️ Не удалось получить расписание. Попробуй позже.")


@router.message(Command("ping"))
async def ping(message: Message) -> None:
    await message.answer("🏓 pong")
