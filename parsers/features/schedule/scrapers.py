from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import TypeVar

from bs4 import BeautifulSoup
from dtos import GroupIdDTO
from endpoints import get_search_groups_url
from furl import furl
from infra.client import Client, configs

T = TypeVar("T")


class ScrapingError(Exception):
    pass


class CallWrapABCMeta(ABCMeta):
    def __new__(mcls, name, bases, namespace, **kwargs) -> type:
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        mcls._maybe_wrap_call(cls)
        return cls

    @staticmethod
    def _maybe_wrap_call(cls: type) -> None:
        call_func = cls.__dict__.get("__call__", None)
        if call_func is None:
            return
        if getattr(call_func, "__isabstractmethod__", False):
            return
        if getattr(call_func, "__wrapped_by_meta__", False):
            return

        @wraps(call_func)
        def wrapper(*args, **kwargs):
            try:
                return call_func(*args, **kwargs)
            except Exception as err:
                raise ScrapingError(str(err)) from err

        wrapper.__wrapped_by_meta__ = True
        cls.__call__ = wrapper


class BaseScraper[T](metaclass=CallWrapABCMeta):
    def __init__(self, client: Client) -> None:
        self._client = client

    @abstractmethod
    def __call__(self, *args, **kwargs) -> T:
        raise NotImplementedError


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


if __name__ == "__main__":
    configs1 = configs.ConfigBox(
        client=configs.ClientConfig(furl("https://ruz.spbstu.ru/"), "RuzSPbPU"),
        net=configs.NetConfig(),
        cache=configs.CacheConfig(enabled=True, ttl=10),
        cookie=configs.CookieConfig(),
    )
    with Client(configs1) as main_client:
        scraper = GroupIdScraper(main_client)
        for _i in range(3):
            group_id_dto = scraper("513090240003")
            print(group_id_dto)
            print()
