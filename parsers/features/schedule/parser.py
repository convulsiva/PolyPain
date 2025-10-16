import datetime as dt
from functools import wraps

from dtos import DayDTO, WeekScheduleDTO
from infra.client import Client
from infra.client.configs import ConfigBox

from scrapers import (
    DailyScheduleScraper,
    GroupExistenceScraper,
    GroupIdScraper,
    WeekScheduleScraper,
)


class ScheduleParser:
    def __init__(self, configs: ConfigBox) -> None:
        self._client = Client(configs)
        self._group_id_scraper = GroupIdScraper(self._client)
        self._group_existence_scraper = GroupExistenceScraper(self._client)
        self._week_schedule_scraper = WeekScheduleScraper(self._client)
        self._daily_schedule_scraper = DailyScheduleScraper(self._client)

    @wraps(GroupIdScraper.__call__)
    def get_group_id(self, name: str) -> int:
        return self._group_id_scraper(name)

    @wraps(GroupExistenceScraper.__call__)
    def group_exist(self, name: str, strict: bool = True) -> bool | tuple[str, ...]:
        return self._group_existence_scraper(name, strict)

    @wraps(WeekScheduleScraper.__call__)
    def get_week_schedule(self, name: str, date: str | dt.date | None = None) -> WeekScheduleDTO:
        return self._week_schedule_scraper(name, date)

    @wraps(DailyScheduleScraper.__call__)
    def get_daily_schedule(self, name: str, date: str | dt.date) -> DayDTO:
        return self._daily_schedule_scraper(name, date)
