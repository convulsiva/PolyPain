from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.infra.repositories.user import UserRepository
from bot.services.schedule import ScheduleService
from bot.telegram.keyboards.week import week_keyboard
from bot.utils.schedule_formatter import format_day
from bot.utils.week_formatter import format_week
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
        day = await schedule_service.get_today(group)
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
        day = await schedule_service.get_tomorrow(group)
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


@router.message(Command("week"))
async def week(message: Message, users_repo: UserRepository) -> None:
    group = await users_repo.get_group(message.chat.id)

    if not group:
        await message.answer("❌ Группа не указана.\n\n<code>/setgroup 5130902/40003</code>")
        return

    parts = message.text.split(maxsplit=1)
    offset = 0

    if len(parts) == 2:
        arg = parts[1].lower()

        if arg == "next":
            offset = 1
        elif arg == "prev":
            offset = -1
        else:
            await message.answer(
                "❌ Неверный аргумент.\n\n"
                "Используй:\n"
                "<code>/week</code>\n"
                "<code>/week next</code>\n"
                "<code>/week prev</code>"
            )
            return

    try:
        days = await schedule_service.get_week(group, offset)

        if not days:
            await message.answer("🎉 <b>На этой неделе пар нет</b>")
            return

        title = "📅 <b>Текущая неделя</b>"
        if offset == 1:
            title = "➡️ <b>Следующая неделя</b>"
        elif offset == -1:
            title = "⬅️ <b>Предыдущая неделя</b>"

        await message.answer(
            f"{title}\n\n{format_week(days)}",
            reply_markup=week_keyboard(offset),
        )

    except GroupNotFoundError:
        await message.answer("❌ Группа не найдена.")

    except Exception:
        await message.answer("⚠️ Не удалось получить расписание недели.")


@router.callback_query(lambda c: c.data and c.data.startswith("week:"))
async def week_callback(
    callback: CallbackQuery,
    users_repo: UserRepository,
) -> None:
    group = await users_repo.get_group(callback.message.chat.id)

    if not group:
        await callback.answer("Группа не указана", show_alert=True)
        return

    try:
        offset = int(callback.data.split(":")[1])
    except ValueError:
        await callback.answer("Некорректные данные", show_alert=True)
        return

    try:
        days = await schedule_service.get_week(group, offset)

        if not days:
            text = "🎉 <b>На этой неделе пар нет</b>"
        else:
            title = "📅 <b>Текущая неделя</b>"
            if offset > 0:
                title = "➡️ <b>Следующая неделя</b>"
            elif offset < 0:
                title = "⬅️ <b>Предыдущая неделя</b>"

            text = f"{title}\n\n{format_week(days)}"

        await callback.message.edit_text(
            text,
            reply_markup=week_keyboard(offset),
        )
        await callback.answer()

    except Exception:
        await callback.answer("Ошибка при получении расписания", show_alert=True)


@router.message(Command("ping"))
async def ping(message: Message) -> None:
    await message.answer("🏓 pong")
