from bs4 import BeautifulSoup
from dtos import GroupIdDTO
from endpoints import get_search_groups_url
from features.base_scraper import BaseScraper
from furl import furl
from infra.client import Client, configs


class GroupIdScraper(BaseScraper[GroupIdDTO]):
    def __call__(self, external_id: str):
        resp = self._client.request("get", get_search_groups_url(external_id))
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        groups = soup.find("ul", class_="groups-list")
        if groups:
            group = groups.find_all("a")[0]
            internal_id = int(furl(group.get("href")).path.segments[-1])
            return GroupIdDTO(external_id=external_id, internal_id=internal_id)
        raise ValueError(f"Group {external_id} not found")


# class DailyScheduleScraper(BaseScraper[])

if __name__ == "__main__":
    configs1 = configs.ConfigBox(
        client=configs.ClientConfig(furl("https://ruz.spbstu.ru/"), "RuzSPbPU"),
        net=configs.NetConfig(),
        cache=configs.CacheConfig(enabled=True, ttl=10),
        cookie=configs.CookieConfig(),
    )
    with Client(configs1) as main_client:
        scraper = GroupIdScraper(main_client)
        for _i in range(30):
            group_id_dto = scraper("5130902/40003")
            print(group_id_dto)
            print()
