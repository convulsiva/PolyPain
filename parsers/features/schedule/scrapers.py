import datetime as dt

from bs4 import BeautifulSoup
from furl import furl
from infra.client import Client

from ..base_scraper import BaseScraper
from .dtos import DayDTO, WeekScheduleDTO
from .endpoints import get_search_groups_url, get_week_schedule_url
from .exceptions import DayNotFoundError, GroupNotFoundError
from .mappers import map_week_schedule, parse_date


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
        raise GroupNotFoundError(f"Group {name} not found")


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

        :param name:
            The public group name (e.g. "5130902/40003").
        :param date:
            Optional target date within the desired week.
            - If provided as a string (in ISO format, e.g. "2025-10-16"),
              it will be automatically converted to a `datetime.date` object.
            - If provided as a `datetime.date`, it is passed directly.
            - If omitted (`None`), the scraper retrieves the schedule for the current week.
        :return:
            A `WeekScheduleDTO` instance containing the full week's schedule
            corresponding to the week of the provided date (or the current week if not specified).
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
        """
        Retrieve the schedule for a specific day of the given group.

        Fetches the full weekly schedule using `WeekScheduleScraper` and extracts
        the day matching the specified date.

        :param name:
            The name of the group whose schedule should be retrieved.
        :param date:
            The target date for which to find the schedule.
            Can be provided either as a string in ISO format (YYYY-MM-DD)
            or as a `datetime.date` object.
        :return:
            A `DayDTO` instance representing the schedule for the specified day.
        :raises DayNotFoundError:
            If the requested date is not found within the retrieved weekly schedule.
        :raises ScrapingError:
            If a network or parsing error occurs during the scraping process.
        """
        if isinstance(date, str):
            date: dt.date = parse_date(date)
        week_schedule = self._week_schedule_scraper(name, date)
        for day in week_schedule.days:
            if day.date == date:
                return day
        raise DayNotFoundError(f"Could not find day on date {date}")
