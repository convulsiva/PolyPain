from requests import Session as NotCachedSession
from requests_cache import CachedSession
from typing import Mapping


SessionLike = NotCachedSession | CachedSession
ProxyLike = str | Mapping[str, str] | None
CookiesLike = ...

