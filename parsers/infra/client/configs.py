from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from http.cookiejar import CookieJar
from os import PathLike

from furl import furl
from urllib3.util.retry import Retry

from .type_defs import ProxyLike


@dataclass(slots=True)
class ClientConfig:
    base_url: furl  # Maybe remove from here
    name: str

    def __post_init__(self):
        self.base_url = furl(self.base_url).remove(fragment=True, args=True)


@dataclass(slots=True)
class NetConfig:
    retry: Retry = field(
        default_factory=lambda: Retry(
            total=3,
            connect=None,  # if None connect = total
            read=None,  # if None read = total
            backoff_factor=0.5,
            allowed_methods=("GET", "HEAD"),
            status_forcelist=(429, 500, 502, 503, 504),
        )
    )
    timeout: float = 5.0
    headers: dict[str, str] = field(
        default_factory=lambda: {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    )
    user_agent: str | None = None  # if None use random user agent
    proxy_strategy: Callable[[str], ProxyLike] | None = None


@dataclass(slots=True)
class CacheConfig:
    enabled: bool = False
    automatic_prune_cache: bool = True
    ttl: int = -1  # Immortal cache
    name: str | None = None
    cache_control: bool = False  # Don't respect server cache
    backend: str = "sqlite"


@dataclass(slots=True)
class CookieConfig:
    initial: Mapping[str, str] | CookieJar | None = None
    file: PathLike[str] | str | None = None


class ConfigBox:
    def __init__(
        self,
        client: ClientConfig,
        net: NetConfig,
        cache: CacheConfig,
        cookie: CookieConfig,
    ) -> None:
        self.client = client
        self.net = net
        self.cache = cache
        self.cookie = cookie
