from ...infra.client import configs
from ..base_parser import BaseParser
from .scrapers import (
    DailyScheduleScraper,
    GroupExistenceScraper,
    WeekScheduleScraper,
)


class ScheduleParser(BaseParser):
    def __init__(self, config_box: configs.ConfigBox) -> None:
        super().__init__(config_box)
        self.group_exist = GroupExistenceScraper(self._client)
        self.get_week_schedule = WeekScheduleScraper(self._client)
        self.get_daily_schedule = DailyScheduleScraper(self._client)
