import asyncio
import datetime as dt

from bot.utils.ttl_cache import TTLCache
from parsers.features.schedule import schedule_parser

CACHE_TTL_SECONDS = 300  # 5 минут


class ScheduleService:
    def __init__(self) -> None:
        self._cache = TTLCache(CACHE_TTL_SECONDS)

    def clear_cache_for_group(self, group: str) -> None:
        keys_to_delete = [
            key for key in self._cache._data if isinstance(key, tuple) and key[1] == group
        ]

        for key in keys_to_delete:
            self._cache._data.pop(key, None)

    async def get_today(self, group: str):
        key = ("today", group)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        today = dt.date.today()
        result = await asyncio.to_thread(
            schedule_parser.get_daily_schedule,
            group,
            today,
        )
        self._cache.set(key, result)
        return result

    async def get_tomorrow(self, group: str):
        key = ("tomorrow", group)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        tomorrow = dt.date.today() + dt.timedelta(days=1)
        result = await asyncio.to_thread(
            schedule_parser.get_daily_schedule,
            group,
            tomorrow,
        )
        self._cache.set(key, result)
        return result

    async def get_week(self, group: str, offset_weeks: int = 0):
        key = ("week", group, offset_weeks)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        base_date = dt.date.today() + dt.timedelta(weeks=offset_weeks)
        week = await asyncio.to_thread(
            schedule_parser.get_week_schedule,
            group,
            base_date,
        )
        self._cache.set(key, week.days)
        return week.days
