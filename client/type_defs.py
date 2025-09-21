from requests import Session as NotCachedSession
from requests.cookies import RequestsCookieJar
from http.cookiejar import CookieJar
from os import PathLike
from requests_cache import CachedSession
from typing import Mapping

SessionLike = NotCachedSession | CachedSession
ProxyLike = str | Mapping[str, str] | None
CookiesLike = Mapping[str, str] | CookieJar | RequestsCookieJar | PathLike[str] | str | None
