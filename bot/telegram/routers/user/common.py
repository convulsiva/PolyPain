from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.infra.repositories.user import UserRepository
from bot.services.schedule import ScheduleService
from bot.telegram.keyboards.main_menu import main_menu_keyboard
from bot.telegram.keyboards.week import week_keyboard
from bot.utils.schedule_formatter import format_day
from bot.utils.week_formatter import format_week

router = Router()
schedule_service = ScheduleService()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "👋 <b>PolyPain</b>\n\nИспользуй кнопки ниже 👇",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("setgroup"))
async def set_group(message: Message, users_repo: UserRepository) -> None:
    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:
        await message.answer(
            "❌ Укажи группу.\n\n<code>/setgroup 5130902/40003</code>",
            reply_markup=main_menu_keyboard(),
        )
        return

    group = parts[1].strip()

    if len(group) < 5 or " " in group:
        await message.answer(
            "❌ Некорректный формат группы.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await users_repo.set_group(message.chat.id, group)
    schedule_service.clear_cache_for_group(group)

    await message.answer(
        f"✅ Группа сохранена: <b>{group}</b>",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("today"))
async def today(message: Message, users_repo: UserRepository) -> None:
    group = await users_repo.get_group(message.chat.id)

    if not group:
        await message.answer(
            "❌ Сначала задай группу через /setgroup",
            reply_markup=main_menu_keyboard(),
        )
        return

    try:
        day = await schedule_service.get_today(group)
        await message.answer(
            "📅 <b>Сегодня</b>\n\n" + format_day(day),
            reply_markup=main_menu_keyboard(),
        )
    except Exception:
        await message.answer(
            "⚠️ Не удалось получить расписание.",
            reply_markup=main_menu_keyboard(),
        )


@router.message(Command("tomorrow"))
async def tomorrow(message: Message, users_repo: UserRepository) -> None:
    group = await users_repo.get_group(message.chat.id)

    if not group:
        await message.answer(
            "❌ Сначала задай группу через /setgroup",
            reply_markup=main_menu_keyboard(),
        )
        return

    try:
        day = await schedule_service.get_tomorrow(group)
        await message.answer(
            "⏭ <b>Завтра</b>\n\n" + format_day(day),
            reply_markup=main_menu_keyboard(),
        )
    except Exception:
        await message.answer(
            "⚠️ Не удалось получить расписание.",
            reply_markup=main_menu_keyboard(),
        )


@router.message(Command("week"))
async def week(message: Message, users_repo: UserRepository) -> None:
    group = await users_repo.get_group(message.chat.id)

    if not group:
        await message.answer(
            "❌ Сначала задай группу через /setgroup",
            reply_markup=main_menu_keyboard(),
        )
        return

    try:
        days = await schedule_service.get_week(group)

        if not days:
            await message.answer("🎉 <b>На этой неделе пар нет</b>")
            return

        await message.answer(
            "📆 <b>Текущая неделя</b>\n\n" + format_week(days),
            reply_markup=week_keyboard(0),  # ✅ INLINE
        )
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
            if offset == 0:
                title = "📆 <b>Текущая неделя</b>"
            elif offset > 0:
                title = "➡️ <b>Следующая неделя</b>"
            else:
                title = "⬅️ <b>Предыдущая неделя</b>"

            text = f"{title}\n\n{format_week(days)}"

        await callback.message.edit_text(
            text,
            reply_markup=week_keyboard(offset),
        )
        await callback.answer()

    except Exception:
        await callback.answer(
            "Ошибка при получении расписания",
            show_alert=True,
        )


@router.message()
async def reply_menu_handler(
    message: Message,
    users_repo: UserRepository,
) -> None:
    text = message.text

    if text not in {"📅 Сегодня", "⏭ Завтра", "📆 Неделя"}:
        return

    group = await users_repo.get_group(message.chat.id)
    if not group:
        await message.answer(
            "❌ Сначала задай группу через /setgroup",
            reply_markup=main_menu_keyboard(),
        )
        return

    try:
        if text == "📅 Сегодня":
            day = await schedule_service.get_today(group)
            await message.answer(
                "📅 <b>Сегодня</b>\n\n" + format_day(day),
                reply_markup=main_menu_keyboard(),
            )

        elif text == "⏭ Завтра":
            day = await schedule_service.get_tomorrow(group)
            await message.answer(
                "⏭ <b>Завтра</b>\n\n" + format_day(day),
                reply_markup=main_menu_keyboard(),
            )

        elif text == "📆 Неделя":
            days = await schedule_service.get_week(group)

            if not days:
                await message.answer("🎉 <b>На этой неделе пар нет</b>")
                return

            await message.answer(
                "📆 <b>Текущая неделя</b>\n\n" + format_week(days),
                reply_markup=week_keyboard(0),  # ✅ INLINE
            )

    except Exception:
        await message.answer(
            "⚠️ Не удалось получить расписание.",
            reply_markup=main_menu_keyboard(),
        )
