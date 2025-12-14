import datetime as dt

from parsers.features.schedule import schedule_parser


class ScheduleService:
    def get_today(self, group: str):
        today = dt.date.today()
        return schedule_parser.get_daily_schedule(group, today)

    def get_tomorrow(self, group: str):
        tomorrow = dt.date.today() + dt.timedelta(days=1)
        return schedule_parser.get_daily_schedule(group, tomorrow)

    def get_week(self, group: str, offset_weeks: int = 0):
        base_date = dt.date.today() + dt.timedelta(weeks=offset_weeks)
        week = schedule_parser.get_week_schedule(group, base_date)
        return week.days
