from bs4 import BeautifulSoup
from requests import Session as NotCachedSession, Response
from requests_cache import CachedSession
from furl import furl
from fake_useragent import UserAgent
from typing import Final, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

SessionLike = Union[NotCachedSession, CachedSession]


@dataclass
class CacheConfig:
    enabled: bool = False
    ttl: int = -1  # Immortal cache
    name: Optional[str] = None
    backend: str = "sqlite"


class Parser(ABC):
    _UA: Final[UserAgent] = UserAgent()

    def __init__(
            self,
            base_url: str,
            parser_name: str,
            cache_config: Optional[CacheConfig] = None
    ) -> None:
        if cache_config is None: cache_config = CacheConfig()
        self._base_url = furl(base_url)
        self._parser_name = parser_name
        self._cache_config = cache_config
        self._session: Optional[SessionLike] = None
        self._set_session()

    def _set_session(self) -> None:
        if self._session is not None: self.close()
        if self._cache_config.enabled:
            self._session = CachedSession(
                self._cache_config.name or self._parser_name,
                expire_after=self._cache_config.ttl
            )
        else:
            self._session = NotCachedSession()

    def disable_cache(self) -> None:
        # Close current session!
        self._cache_config.enabled = False
        self._set_session()

    def enable_cache(self, cache_config: Optional[CacheConfig] = None) -> None:
        # Close current session!
        if cache_config is None:
            cache_config = CacheConfig(enabled=True)
        assert cache_config.enabled, f"Caching should be enabled! {cache_config}"
        self._cache_config = cache_config
        self._set_session()

    def prune_cache(self) -> None:
        if isinstance(self._session, CachedSession):
            self._session.cache.remove_expired_responses()

    def clear_cache(self) -> None:
        if isinstance(self._session, CachedSession):
            self._session.cache.clear()

    def _get_response(self, url: str) -> Response:
        # add timeout
        response = self._session.get(self._base_url / url)
        response.encoding = "utf-8"
        return response

    def _get_soup(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(self._get_response(url).text, "lxml")

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "Parser":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        use_cache = "Yes" if self._cache_config.enabled else "No"
        cache_ttl = "immortal" if self._cache_config.ttl < 0 else self._cache_config.ttl
        return f"<Parser object: {self._parser_name}, use_cache: {use_cache}, cache_ttl: {cache_ttl}>"
