from datetime import datetime, timedelta
import logging

from bot.infra.repositories.user import UserRepository
from bot.services.schedule import ScheduleService

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self) -> None:
        self.schedule_service = ScheduleService()

        # 🔐 Анти-дубль: запоминаем, что уже отправили
        self._sent: set[tuple[int, str, datetime]] = set()

    async def check_and_notify(
        self,
        bot,
        users_repo: UserRepository,
        minutes_before: int,
    ) -> None:
        now = datetime.now()

        users = await users_repo.get_all_with_notifications()

        for user in users:
            chat_id = user.id
            group = user.group

            try:
                day = await self.schedule_service.get_today(group)
            except Exception as e:
                logger.warning(
                    "Failed to get schedule for group %s: %s",
                    group,
                    e,
                )
                continue

            if not day or not day.lessons:
                continue

            for lesson in day.lessons:
                lesson_dt = datetime.combine(
                    now.date(),
                    lesson.time_start,
                )

                delta = lesson_dt - now

                if not (timedelta(0) < delta <= timedelta(minutes=minutes_before)):
                    continue

                key = (chat_id, group, lesson_dt)

                # 🔐 Уже отправляли → пропускаем
                if key in self._sent:
                    continue

                text = (
                    "🔔 <b>Скоро пара!</b>\n\n"
                    f"📚 <b>{lesson.subject}</b>\n"
                    f"🕘 {lesson.time_start.strftime('%H:%M')}–"
                    f"{lesson.time_end.strftime('%H:%M')}\n"
                    f"📍 {lesson.place or '—'}"
                )

                try:
                    await bot.send_message(chat_id, text)
                    self._sent.add(key)

                    logger.info(
                        "Notification sent to user=%s group=%s lesson=%s",
                        chat_id,
                        group,
                        lesson_dt,
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to send notification to %s: %s",
                        chat_id,
                        e,
                    )
