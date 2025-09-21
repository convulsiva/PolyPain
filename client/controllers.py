from os import PathLike
from managers import SessionManager
from configs import CacheConfig, ConfigBox
from exceptions import CacheDisabledError
from typing import Mapping
from type_defs import CachedSession, NotCachedSession, CookiesLike
from http.cookiejar import CookieJar
from requests.utils import dict_from_cookiejar
from requests.cookies import RequestsCookieJar
from pathlib import Path
from http.cookiejar import MozillaCookieJar


class BaseController:
    def __init__(self,
                 session_manager: SessionManager,
                 configs: ConfigBox) -> None:
        self._session_manager = session_manager
        self._configs = configs


class CacheController(BaseController):
    def enable(self, cache_config: CacheConfig | None = None) -> None:
        # Close current session!
        if cache_config:
            if not cache_config.enabled:
                raise CacheDisabledError("In CacheConfig, the enabled field is False")
            self._configs.cache = cache_config
        else:
            self._configs.cache.enabled = True
        self._session_manager.switch_cache(self._configs.cache)

    def disable(self) -> None:
        # Close current session!
        self._configs.cache.enabled = False
        self._session_manager.switch_cache(self._configs.cache)

    def prune(self) -> None:
        if isinstance(self._session_manager.session, CachedSession):
            self._session_manager.session.cache.remove_expired_responses()

    def clear(self) -> None:
        if isinstance(self._session_manager.session, CachedSession):
            self._session_manager.session.cache.clear()


class CookieController(BaseController):
    def get(self) -> dict[str, str]:
        return dict_from_cookiejar(self._session_manager.session.cookies)

    def save(self, file_path: PathLike[str] | None = None) -> None:
        file_path = file_path or self._configs.cookie.file
        if file_path is None:
            raise FileNotFoundError("No cookie file path provided")
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        jar = MozillaCookieJar(file_path)
        for c in self._session_manager.session.cookies:
            jar.set_cookie(c)
        jar.save(ignore_discard=True, ignore_expires=True)

    def update(self,
               cookies: CookiesLike = None,
               clear_current_cookies: bool = False) -> None:
        jar: RequestsCookieJar = self._session_manager.session.cookies
        if clear_current_cookies: self.clear()
        if cookies is None: return None
        if isinstance(cookies, Mapping):
            jar.update(dict(cookies))
        elif isinstance(cookies, CookieJar):
            jar.update(cookies)
        elif isinstance(cookies, (PathLike, str)):
            path = Path(cookies)
            if not path.exists():
                raise FileNotFoundError(f"No such cookie file: {path}")
            file_jar = MozillaCookieJar(str(path))
            file_jar.load(ignore_discard=True, ignore_expires=True)
            jar.update(file_jar)
        else:
            raise TypeError(f"Cookies must be {CookiesLike}, got {type(cookies)}")

    def clear(self,
                      domain: str | None = None,
                      path: str | None = None,
                      name: str | None = None) -> None:
        self._session_manager.session.cookies.clear(domain, path, name)
