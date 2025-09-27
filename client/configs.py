from http.cookiejar import CookieJar
from furl import furl
from typing import Optional, Union, Mapping, FrozenSet, Callable
from dataclasses import dataclass, field
from os import PathLike
from type_defs import ProxyLike


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
    user_agent: Optional[str] = None  # if None use random user agent
    proxy_strategy: Callable[[str], ProxyLike] | None = None


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


class ConfigBox:
    def __init__(self,
                 client: ClientConfig,
                 net: NetConfig,
                 cache: CacheConfig,
                 cookie: CookieConfig) -> None:
        self.client = client
        self.net = net
        self.cache = cache
        self.cookie = cookie
