from infra.client import Client
from infra.client.configs import ConfigBox

from .scrapers import (
    DailyScheduleScraper,
    GroupExistenceScraper,
    GroupIdScraper,
    WeekScheduleScraper,
)


class ScheduleParser:
    def __init__(self, configs: ConfigBox) -> None:
        self._client = Client(configs)
        self.get_group_id = GroupIdScraper(self._client)
        self.group_exist = GroupExistenceScraper(self._client)
        self.get_week_schedule = WeekScheduleScraper(self._client)
        self.get_daily_schedule = DailyScheduleScraper(self._client)
