from datetime import datetime, timedelta
import logging

from bot.infra.repositories.user import UserRepository
from bot.services.schedule import ScheduleService

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self) -> None:
        self.schedule_service = ScheduleService()

    async def check_and_notify(
        self,
        bot,
        users_repo: UserRepository,
        minutes_before: int,
    ) -> None:
        """
        Проверяет расписание и отправляет уведомления о начале пар
        пользователям, у которых включены уведомления.
        """

        now = datetime.now()

        # 🔹 Берём ТОЛЬКО пользователей:
        # - с включёнными уведомлениями
        # - с указанной группой
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
                # lesson.start_time — datetime.time
                lesson_datetime = datetime.combine(
                    now.date(),
                    lesson.start_time,
                )

                delta = lesson_datetime - now

                # ⏰ Проверяем интервал
                if timedelta(0) < delta <= timedelta(minutes=minutes_before):
                    text = (
                        "🔔 <b>Скоро пара!</b>\n\n"
                        f"📚 <b>{lesson.subject}</b>\n"
                        f"🕘 {lesson.start_time.strftime('%H:%M')}–"
                        f"{lesson.end_time.strftime('%H:%M')}\n"
                        f"📍 {lesson.place or '—'}"
                    )

                    try:
                        await bot.send_message(chat_id, text)
                        logger.info(
                            "Notification sent to user %s (%s)",
                            chat_id,
                            group,
                        )
                    except Exception as e:
                        logger.warning(
                            "Failed to send notification to %s: %s",
                            chat_id,
                            e,
                        )
