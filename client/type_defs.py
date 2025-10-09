from collections.abc import Mapping
from http.cookiejar import CookieJar
from os import PathLike

from requests import Session as NotCachedSession
from requests.cookies import RequestsCookieJar
from requests_cache import CachedSession

SessionLike = NotCachedSession | CachedSession
ProxyLike = str | Mapping[str, str] | None
CookiesLike = Mapping[str, str] | CookieJar | RequestsCookieJar | PathLike[str] | str | None
