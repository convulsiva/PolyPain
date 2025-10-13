from bs4 import BeautifulSoup
from endpoints import get_search_groups_url
from features.base_scraper import BaseScraper
from furl import furl
from infra.client import Client, configs


class GroupIdScraper(BaseScraper[int]):
    def __call__(self, name: str) -> int:
        resp = self._client.request("get", get_search_groups_url(name))
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        groups = soup.find("ul", class_="groups-list")
        if groups:
            group = groups.find_all("a")[0]
            id_ = furl(group.get("href")).path.segments[-1]
            return int(id_)
        raise ValueError(f"Group {name} not found")


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
        resp = self._client.request("get", get_search_groups_url(name))
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        groups = soup.find("ul", class_="groups-list")
        if groups is None:
            return False
        if strict:
            return any(name == a.text.strip() for a in groups.find_all("a"))
        return tuple(a.text.strip() for a in groups.find_all("a"))


# class DailyScheduleScraper(BaseScraper[])


if __name__ == "__main__":
    configs1 = configs.ConfigBox(
        client=configs.ClientConfig(furl("https://ruz.spbstu.ru/"), "RuzSPbPU"),
        net=configs.NetConfig(),
        cache=configs.CacheConfig(enabled=True, ttl=10),
        cookie=configs.CookieConfig(),
    )
    with Client(configs1) as main_client:
        sc = GroupExistenceScraper(main_client)
        print(sc("5130902", strict=False))
