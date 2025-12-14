import datetime

from furl import furl

BASE_URL = "https://ruz.spbstu.ru"


def get_search_groups_url(external_id: str) -> str:
    return str(furl(BASE_URL).add(path="search/groups").add(args={"q": external_id}))


def get_week_schedule_url(group_id: int, date: datetime.date | None = None) -> str:
    url = furl(BASE_URL).add(path=f"/api/v1/ruz/scheduler/{group_id}")
    if date:
        url.add(args={"date": date.strftime("%Y-%m-%d")})
    return str(url)
