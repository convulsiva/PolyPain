from ...infra.client import Client, configs
from .scrapers import (
    DailyScheduleScraper,
    GroupExistenceScraper,
    WeekScheduleScraper,
)


class ScheduleParser:
    def __init__(self, config_box: configs.ConfigBox) -> None:
        self._client = Client(config_box)
        self.group_exist = GroupExistenceScraper(self._client)
        self.get_week_schedule = WeekScheduleScraper(self._client)
        self.get_daily_schedule = DailyScheduleScraper(self._client)
