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
from abc import ABC
from os import PathLike
from pathlib import Path

SessionLike = Union[NotCachedSession, CachedSession]


@dataclass(slots=True)
class ClientConfig:
    base_url: furl
    name: str

    def __post_init__(self):
        self.base_url = furl(self.base_url).remove(fragment=True, args=True)


@dataclass(slots=True)
class NetConfig:
    timeout: float = 5.0
    retries_total: int = 3
    retries_connect: Optional[int] = None   # if None retries_connect = retries_total
    retries_read: Optional[int] = None      # if None retries_read = retries_total
    backoff_factor: float = 0.5
    allowed_methods: tuple[str, ...] = ("GET", "HEAD")
    status_forcelist: FrozenSet[int] = frozenset({429, 500, 502, 503, 504})

    headers: dict[str, str] = field(default_factory=dict)
    proxies: dict[str, str] = field(default_factory=dict)  # {"http": "...", "https": "..."}
    user_agent: Optional[str] = None  # if None use random user agent


@dataclass(slots=True)
class CacheConfig:
    enabled: bool = False
    ttl: int = -1  # Immortal cache
    name: Optional[str] = None
    cache_control: bool = False  # Don't respect server cache
    backend: str = "sqlite"


@dataclass(slots=True)
class CookieConfig:
    initial: Optional[Union[Mapping[str, str], CookieJar]] = None
    file: Optional[Union[PathLike[str], str]] = None


class Client(ABC):
    _UA: Final[UserAgent] = UserAgent()

    def __init__(
            self,
            client_config: ClientConfig,
            net_config: Optional[NetConfig] = None,
            cache_config: Optional[CacheConfig] = None,
            cookie_config: Optional[CookieConfig] = None
    ) -> None:
        if net_config is None: net_config = NetConfig()
        if cache_config is None: cache_config = CacheConfig()
        if cookie_config is None: cookie_config = CookieConfig()

        self._base_url = client_config.base_url

        self._client_config = client_config
        self._net_config = net_config
        self._cache_config = cache_config
        self._cookie_config = cookie_config

        self._session: Optional[SessionLike] = None
        self.__set_session()

    def __set_session(self) -> None:
        if self._session is not None: self.close()
        if self._cache_config.enabled:
            self._session = CachedSession(
                cache_name=self._cache_config.name or self._client_config.name,
                backend=self._cache_config.backend,
                expire_after=self._cache_config.ttl,
                cache_control=self._cache_config.cache_control
            )
        else:
            self._session = NotCachedSession()
        self.set_default_headers()
        self._set_adapter(self._get_retry_adapter())
        if self._cookie_config.file:
            self.update_cookies(self._cookie_config.file)
        if self._cookie_config.initial:
            self.update_cookies(self._cookie_config.initial)
        if self._net_config.proxies:
            self.set_proxies(self._net_config.proxies)

    def _get_retry_adapter(self) -> HTTPAdapter:
        return HTTPAdapter(max_retries=Retry(
            total=self._net_config.retries_total,
            connect=self._net_config.retries_connect,
            read=self._net_config.retries_read,
            backoff_factor=self._net_config.backoff_factor,
            status_forcelist=self._net_config.status_forcelist,
            allowed_methods=self._net_config.allowed_methods,
            respect_retry_after_header=True,
            raise_on_status=False
        ))

    def _set_adapter(self, adapter: HTTPAdapter) -> None:
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def _clear_adapters(self) -> None:
        for adapter in self._session.adapters.values():
            adapter.close()
        self._session.adapters.clear()
        self._session.mount("http://", HTTPAdapter())
        self._session.mount("https://", HTTPAdapter())

    def set_default_headers(self, extra: Optional[dict] = None) -> None:
        self._session.headers.update({
            "User-Agent": self._UA.random if self._net_config.user_agent is None else self._net_config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
        if extra:
            self._session.headers.update(extra)

    def get_default_headers(self, extra: Optional[dict] = None) -> dict[str, str]:
        headers = dict(self._session.headers)
        if extra:
            headers.update(extra)
        return headers

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

    def save_cookies(self, file_path: Optional[str] = None) -> None:
        file_path = file_path or self._cookie_config.file
        assert file_path, "No cookie file path provided"
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        jar = MozillaCookieJar(file_path)
        for c in self._session.cookies:
            jar.set_cookie(c)
        jar.save(ignore_discard=True, ignore_expires=True)

    def update_cookies(
            self,
            cookies: Union[Mapping[str, str], CookieJar, RequestsCookieJar, PathLike[str], str, None] = None,
            clear_current_cookies: bool = False,
    ) -> None:
        jar: RequestsCookieJar = self._session.cookies
        if clear_current_cookies: self.clear_cookies()
        if cookies is None: return None
        if isinstance(cookies, Mapping):
            jar.update(dict(cookies))
        elif isinstance(cookies, RequestsCookieJar):
            jar.update(cookies)
        elif isinstance(cookies, CookieJar):
            for c in cookies:
                jar.set_cookie(c)
        elif isinstance(cookies, (PathLike, str)):
            path = Path(cookies)
            assert path.exists(), f"The path to the file does not exist. Now {cookies = }"
            file_jar = MozillaCookieJar(str(path))
            file_jar.load(ignore_discard=True, ignore_expires=True)
            for c in file_jar:
                jar.set_cookie(c)
        else:
            raise TypeError(
                f"Cookies must be Mapping[str, str] | CookieJar | RequestsCookieJar | PathLike[str], got {type(cookies)}"
            )

    def clear_cookies(self,
                      domain: Optional[str] = None,
                      path: Optional[str] = None,
                      name: Optional[str] = None) -> None:
        self._session.cookies.clear(domain, path, name)

    def set_proxies(self, proxies: Mapping[str, str]):
        assert self._session is not None, "Session is not setup!"
        proxies = dict(proxies)
        self._session.proxies.update(proxies)
        self._net_config.proxies = proxies

    def get_proxies(self) -> dict[str, str]:
        assert self._session is not None, "Session is not setup!"
        return dict(self._session.proxies)

    def close(self) -> None:
        self.prune_cache()
        self._session.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        use_cache = "Yes" if self._cache_config.enabled else "No"
        cache_ttl = "immortal" if self._cache_config.ttl < 0 else self._cache_config.ttl
        return f"<Client object: {self._client_config.name}, use_cache: {use_cache}, cache_ttl: {cache_ttl}>"
