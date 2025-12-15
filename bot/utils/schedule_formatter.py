from parsers.features.schedule.dtos import DayDTO, LessonDTO


def _format_lesson(i: int, lesson: LessonDTO) -> str:
    time = f"{lesson.time_start.strftime('%H:%M')}–{lesson.time_end.strftime('%H:%M')}"
    teachers = ", ".join(t.full_name for t in lesson.teachers) or "—"
    auds = ", ".join(a.name for a in lesson.auditories) or "—"

    return f"<b>{i}. {lesson.name}</b> ({lesson.type_})\n⏰ {time}\n👤 {teachers}\n🏫 {auds}"


def format_day(day: DayDTO) -> str:
    header = f"📅 <b>{day.weekday.value}</b>, {day.date.strftime('%d.%m.%Y')}\n\n"

    if not day.lessons:
        return header + "🎉 <i>Сегодня пар нет</i>"

    body = "\n\n".join(_format_lesson(i + 1, lesson) for i, lesson in enumerate(day.lessons))
    return header + body
