from pprint import pprint

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


# class DailyScheduleScraper(BaseScraper[])


if __name__ == "__main__":
    configs1 = configs.ConfigBox(
        client=configs.ClientConfig(furl("https://ruz.spbstu.ru/"), "RuzSPbPU"),
        net=configs.NetConfig(),
        cache=configs.CacheConfig(enabled=True, ttl=10),
        cookie=configs.CookieConfig(),
    )
    with Client(configs1) as main_client:
        res = main_client.request(
            "get", r"https://ruz.spbstu.ru/api/v1/ruz/scheduler/42733?date=2025-10-17"
        )
        pprint(res.json())
