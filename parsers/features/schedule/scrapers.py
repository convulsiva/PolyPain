import datetime as dt

from bs4 import BeautifulSoup
from dtos import DayDTO, WeekScheduleDTO
from endpoints import get_search_groups_url, get_week_schedule_url
from exceptions import GroupFindError
from features.base_scraper import BaseScraper
from furl import furl
from infra.client import Client, configs
from mappers import map_week_schedule, parse_date


class GroupIdScraper(BaseScraper[int]):
    def __call__(self, name: str) -> int:
        """
        Retrieve the internal group ID by its name.

        Sends a GET request to the group search endpoint, parses the resulting HTML,
        and extracts the numeric group ID from the first matching search result.

        :param name: The group name to search for.
        :return: The internal integer ID of the first matched group.
        :raises ValueError:
            If no group with the given name was found.
        :raises ScrapingError:
            If a network or parsing error occurs during the request.
        """
        resp = self._client.request(method="get", url=get_search_groups_url(name))
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        groups = soup.find("ul", class_="groups-list")
        if groups:
            group = groups.find_all("a")[0]
            id_ = furl(group.get("href")).path.segments[-1]
            return int(id_)
        raise GroupFindError(f"Group {name} not found")


class GroupExistenceScraper(BaseScraper[bool | tuple[str, ...]]):
    def __call__(self, name: str, strict: bool = True) -> bool | tuple[str, ...]:
        """
        Perform a group existence check on the search page.

        Sends a GET request to the group search endpoint and parses the resulting
        HTML to determine whether the specified group name exists.

        :param name: The group name to search for.
        :param strict:
            If True — returns a boolean indicating whether an exact match is found.
            If False — returns a tuple of all group names that contain the search term.
        :return:
            - bool: True if the group exists (when strict=True).
            - tuple[str, ...]: All found group names (when strict=False).
        :raises ScrapingError:
            If a network or parsing error occurs during the request.
        """
        resp = self._client.request(method="get", url=get_search_groups_url(name))
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        groups = soup.find("ul", class_="groups-list")
        if groups is None:
            return False
        if strict:
            return any(name == a.text.strip() for a in groups.find_all("a"))
        return tuple(a.text.strip() for a in groups.find_all("a"))


class WeekScheduleScraper(BaseScraper[WeekScheduleDTO]):
    def __init__(self, client: Client, group_id_scraper: GroupIdScraper | None = None) -> None:
        super().__init__(client)
        self._group_id_scraper = group_id_scraper or GroupIdScraper(client)

    def __call__(self, name: str, date: str | dt.date | None = None) -> WeekScheduleDTO:
        """
        Retrieve a full weekly schedule for the specified group.

        Uses the internal group ID obtained from the GroupIdScraper to build
        a request URL, sends a GET request to the schedule endpoint, and maps
        the received JSON response into a structured WeekScheduleDTO object.

        :param name: The public group name (e.g. "5130902/40003").
        :return: A WeekScheduleDTO instance containing the full week's schedule.
        :raises ScrapingError:
            If a network or parsing error occurs during the request.
        """
        if isinstance(date, str):
            date: dt.date = parse_date(date)
        group_id = self._group_id_scraper(name)
        resp = self._client.request(method="get", url=get_week_schedule_url(group_id, date))
        resp.encoding = "utf-8"
        return map_week_schedule(resp.json())


class DailyScheduleScraper(BaseScraper[DayDTO]):
    def __init__(self, client, week_schedule_scraper: WeekScheduleScraper | None = None) -> None:
        super().__init__(client)
        self._week_schedule_scraper = week_schedule_scraper or WeekScheduleScraper(client)

    def __call__(self, name: str, date: str | dt.date) -> DayDTO:
        if isinstance(date, str):
            date: dt.date = parse_date(date)
        week_schedule = self._week_schedule_scraper(name, date)
        for day in week_schedule.days:
            if day.date == date:
                return day
        raise


if __name__ == "__main__":
    from pprint import pprint

    configs1 = configs.ConfigBox(
        client=configs.ClientConfig(furl("https://ruz.spbstu.ru/"), "RuzSPbPU"),
        net=configs.NetConfig(),
        cache=configs.CacheConfig(enabled=True, ttl=10),
        cookie=configs.CookieConfig(),
    )
    with Client(configs1) as main_client:
        sc = DailyScheduleScraper(main_client)
        pprint(sc("5130902/40003", "2025-10-16"))
