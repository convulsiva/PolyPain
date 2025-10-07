from bs4 import BeautifulSoup
from furl import furl

from client import Client
from typing import TypedDict
from client.configs import ClientConfig, NetConfig, CacheConfig, CookieConfig, ConfigBox


class GroupIdDTO(TypedDict):
    external_id: str  # номер группы, как вводит пользователь
    internal_id: int  # внутренний ID в системе расписания


class GroupIdScraper:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, external_id: str) -> GroupIdDTO:
        resp = self._client.request("get", "search/groups", prepare_kwargs={"params": {"q": external_id}})
        assert resp.status_code == 200
        if hasattr(resp, "from_cache"):
            print(f"from cache = {resp.from_cache}")
        else:
            print("from cache = False")
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        groups = soup.find("ul", class_="groups-list").find_all("a")
        if groups:
            internal_id = int(furl(groups[0].get("href")).path.segments[-1])
            return GroupIdDTO(external_id=external_id,
                              internal_id=internal_id)
        raise ValueError



if __name__ == "__main__":
    configs = ConfigBox(client=ClientConfig(furl("https://ruz.spbstu.ru/"), "RuzSPbPU"),
                        net=NetConfig(),
                        cache=CacheConfig(enabled=True, ttl=10),
                        cookie=CookieConfig())
    with Client(configs) as main_client:
        scraper = GroupIdScraper(main_client)
        for i in range(3):
            group_id_dto: GroupIdDTO = scraper("5130902/40003")
            print(group_id_dto); print()
