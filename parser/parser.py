from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar
from urllib3.util.retry import Retry
from requests import Session as NotCachedSession, Response
from requests.adapters import HTTPAdapter
from requests.utils import cookiejar_from_dict, dict_from_cookiejar
from requests_cache import CachedSession
from http.cookiejar import MozillaCookieJar, CookieJar
from furl import furl
from fake_useragent import UserAgent
from typing import Final, Optional, Union, Any, Mapping, FrozenSet
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from os.path import exists as path_exists

SessionLike = Union[NotCachedSession, CachedSession]


@dataclass(frozen=True, slots=True)
class ParserCoreConfig:
    base_url: str
    name: str


@dataclass(frozen=True, slots=True)
class ParserNetConfig:
    timeout: float = 5.0
    retries_total: int = 3
    retries_connect: Optional[int] = None   # if None retries_connect = retries_total
    retries_read: Optional[int] = None      # if None retries_read = retries_total
    backoff_factor: float = 0.5
    allowed_methods: tuple[str, ...] = ("GET", "HEAD")
    status_forcelist: FrozenSet[int, ...] = frozenset({429, 500, 502, 503, 504})

    headers: Mapping[str, str] = field(default_factory=dict)
    proxies: Mapping[str, str] = field(default_factory=dict)  # {"http": "...", "https": "..."}
    user_agent: Optional[str] = None  # if None use random user agent


@dataclass(slots=True)
class CacheConfig:
    enabled: bool = False
    ttl: int = -1  # Immortal cache
    name: Optional[str] = None
    cache_control: bool = False  # Don't respect server cache
    backend: str = "sqlite"


@dataclass(frozen=True, slots=True)
class CookieConfig:
    initial: Optional[Union[Mapping[str, str], CookieJar]] = None
    file: Optional[str] = None


class Parser(ABC):
    _UA: Final[UserAgent] = UserAgent()

    def __init__(
            self,
            parser_config: ParserCoreConfig,
            net_config: Optional[ParserNetConfig] = None,
            cache_config: Optional[CacheConfig] = None,
            cookie_config: Optional[CookieConfig] = None
    ) -> None:
        if net_config is None: net_config = ParserNetConfig()
        if cache_config is None: cache_config = CacheConfig()
        if cookie_config is None: cookie_config = CookieConfig()

        self._base_url = furl(parser_config.base_url).remove(fragment=True, args=True)

        self._parser_config = parser_config
        self._net_config = net_config
        self._cache_config = cache_config
        self._cookie_config = cookie_config

        self._session: Optional[SessionLike] = None
        self.__set_session()

    def __set_session(self) -> None:
        if self._session is not None: self.close()
        if self._cache_config.enabled:
            self._session = CachedSession(
                cache_name=self._cache_config.name or self._parser_config.name,
                backend=self._cache_config.backend,
                expire_after=self._cache_config.ttl,
                cache_control=self._cache_config.cache_control
            )
        else:
            self._session = NotCachedSession()
        self._session.headers.update({
            "User-Agent": self._UA.random if self._net_config.user_agent is None else self._net_config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
        adapter = HTTPAdapter(max_retries=Retry(
            total=self._net_config.retries_total,
            connect=self._net_config.retries_connect,
            read=self._net_config.retries_read,
            backoff_factor=self._net_config.backoff_factor,
            status_forcelist=self._net_config.status_forcelist,
            allowed_methods=self._net_config.allowed_methods,
        ))
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        self.load_cookies()

    def disable_cache(self) -> None:
        # Close current session!
        self._cache_config.enabled = False
        self.__set_session()

    def enable_cache(self, cache_config: Optional[CacheConfig] = None) -> None:
        # Close current session!
        if cache_config is None:
            cache_config = CacheConfig(enabled=True)
        assert cache_config.enabled, f"Caching should be enabled! Now {cache_config = }"
        self._cache_config = cache_config
        self.__set_session()

    def prune_cache(self) -> None:
        if isinstance(self._session, CachedSession):
            self._session.cache.remove_expired_responses()

    def clear_cache(self) -> None:
        if isinstance(self._session, CachedSession):
            self._session.cache.clear()

    def get_cookies(self) -> dict[str, str]:
        assert self._session is not None, "Session is not setup!"
        return dict_from_cookiejar(self._session.cookies)

    def set_cookies(self, cookies: Union[Mapping[str, str], CookieJar, RequestsCookieJar]) -> None:
        assert isinstance(cookies, (Mapping, CookieJar, RequestsCookieJar)), \
            f"cookies must be Mapping[str, str] | CookieJar | RequestsCookieJar, Now type(cookies) = {type(cookies)}"
        jar: RequestsCookieJar = self._session.cookies

        if isinstance(cookies, Mapping):
            jar.update(dict(cookies))
        elif isinstance(cookies, RequestsCookieJar):
            jar.update(cookies)
        elif isinstance(cookies, CookieJar):
            for c in cookies:
                jar.set_cookie(c)


    def save_cookies(self, file_path: Optional[str] = None) -> None:
        file_path = file_path or self._cookie_config.file
        assert file_path, "No cookie file path provided"
        jar = MozillaCookieJar(file_path)
        for c in self._session.cookies:
            jar.set_cookie(c)
        jar.save(ignore_discard=True, ignore_expires=True)

    def load_cookies(self, file_path: Optional[str] = None) -> None:
        file_path = file_path or self._cookie_config.file
        if not file_path or not path_exists(file_path): return None
        jar = MozillaCookieJar(file_path)
        jar.load(ignore_discard=True, ignore_expires=True)
        for c in jar:
            self._session.cookies.set_cookie(c)

    def set_poxy(self): pass
    def get_poxy(self): pass

    def _get_response(self, url: str, *args, **kwargs) -> Response:
        url = (self._base_url / url).url
        response = self._session.get(url, *args, **kwargs)
        response.encoding = "utf-8"
        return response

    def _get_soup(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(self._get_response(url).text, "lxml")

    def close(self) -> None:
        self.prune_cache()
        self._session.close()

    def __enter__(self) -> "Parser":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        use_cache = "Yes" if self._cache_config.enabled else "No"
        cache_ttl = "immortal" if self._cache_config.ttl < 0 else self._cache_config.ttl
        return f"<Parser object: {self._parser_config.name}, use_cache: {use_cache}, cache_ttl: {cache_ttl}>"
