from bot.utils.schedule_formatter import format_day
from parsers.features.schedule.dtos import DayDTO


def format_week(days: list[DayDTO]) -> str:
    if not days:
        return "🎉 <b>На этой неделе пар нет</b>"

    parts: list[str] = []

    for day in days:
        parts.append(format_day(day))

    return "\n\n━━━━━━━━━━━━━━\n\n".join(parts)
