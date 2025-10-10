from collections.abc import Callable, Iterable, Mapping
from http.cookiejar import CookieJar, MozillaCookieJar
from os import PathLike
from pathlib import Path

from configs import CacheConfig, ConfigBox
from exceptions import CacheDisabledError
from managers import SessionManager
from requests.adapters import HTTPAdapter
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict
from requests.utils import dict_from_cookiejar
from type_defs import CookiesLike, ProxyLike, SessionLike
from urllib3.util.retry import Retry


class BaseController:
    def __init__(self, session_manager: SessionManager, configs: ConfigBox) -> None:
        self._session_manager = session_manager
        self._configs = configs

    @property
    def _session(self) -> SessionLike:
        return self._session_manager.session


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
        if hasattr(self._session, "cache"):
            self._session.cache.delete(expired=True)

    def clear(self) -> None:
        if hasattr(self._session, "cache"):
            self._session.cache.clear()


class CookiesController(BaseController):
    @property
    def _cookies(self) -> RequestsCookieJar:
        return self._session.cookies

    def get_all(self) -> dict[str, str]:
        return dict_from_cookiejar(self._cookies)

    def save(self, file_path: PathLike[str] | None = None) -> None:
        file_path = file_path or self._configs.cookie.file
        if file_path is None:
            raise ValueError("No cookie file path provided")
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        jar = MozillaCookieJar(file_path)
        for c in self._cookies:
            jar.set_cookie(c)
        jar.save(ignore_discard=True, ignore_expires=True)

    def update(self, cookies: CookiesLike = None, clear_current_cookies: bool = False) -> None:
        jar: RequestsCookieJar = self._cookies
        if clear_current_cookies:
            self.clear()
        if cookies is None:
            return
        if isinstance(cookies, Mapping):
            jar.update(dict(cookies))
        elif isinstance(cookies, RequestsCookieJar):
            jar.update(cookies)
        elif isinstance(cookies, CookieJar):
            for c in cookies:
                jar.set_cookie(c)
        elif isinstance(cookies, (PathLike, str)):
            path = Path(cookies)
            if not path.exists():
                raise FileNotFoundError(f"No such cookie file: {path}")
            file_jar = MozillaCookieJar(str(path))
            file_jar.load(ignore_discard=True, ignore_expires=True)
            for c in file_jar:
                jar.set_cookie(c)
        else:
            raise TypeError(f"Cookies must be {CookiesLike}, got {type(cookies)}")

    def clear(
        self,
        domain: str | None = None,
        path: str | None = None,
        name: str | None = None,
    ) -> None:
        self._cookies.clear(domain, path, name)


class HeadersController(BaseController):
    @property
    def _headers(self) -> CaseInsensitiveDict:
        return self._session.headers

    def get_all(self) -> dict[str, str]:
        return dict(self._headers)

    def get(self, name: str, default: str | None = None) -> str | None:
        return self._headers.get(name, default)

    def set(self, name: str, value: str) -> None:
        self._headers[name] = value

    def update(self, extra: Mapping[str, str] | None = None, **kwargs: str) -> None:
        if extra:
            self._headers.update(dict(extra))
        if kwargs:
            self._headers.update(kwargs)

    def remove(self, name: str) -> None:
        self._headers.pop(name, None)

    def clear(self) -> None:
        self._headers.clear()


class ProxiesController(BaseController):
    @property
    def _proxies(self) -> dict:
        return self._session.proxies

    def get_all(self) -> dict[str, str]:
        return dict(self._proxies)

    def get(self, scheme: str, default: str | None = None) -> str | None:
        return self._proxies.get(scheme, default)

    def set(self, scheme: str, url: str) -> None:
        self._proxies[scheme] = url

    def update(self, mapping: Mapping[str, str]) -> None:
        self._proxies.update(dict(mapping))

    def remove(self, scheme: str) -> None:
        self._proxies.pop(scheme, None)

    def clear(self) -> None:
        self._proxies.clear()

    def set_strategy(self, fn: Callable[[str], ProxyLike] | None) -> None:
        """Saves the strategy to the config; send() will read it from NetConfig.proxy_strategy."""
        self._configs.net.proxy_strategy = fn

    def get_strategy(self) -> Callable[[str], ProxyLike] | None:
        return self._configs.net.proxy_strategy

    def disable_strategy(self) -> None:
        self.set_strategy(None)


class AdaptersController(BaseController):
    @property
    def _adapters(self) -> dict[str, HTTPAdapter]:
        return self._session.adapters

    def get_all(self) -> dict[str, HTTPAdapter]:
        return dict(self._adapters)

    def get(self, prefix: str, default: HTTPAdapter | None = None) -> HTTPAdapter | None:
        return self._adapters.get(prefix, default)

    def mount(
        self,
        prefix: str,
        *,
        retry: Retry | None = None,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ) -> None:
        adapter = HTTPAdapter(
            max_retries=retry or Retry(0),
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
        )
        self._session.mount(prefix, adapter)

    def reset(
        self,
        prefixes: Iterable[str] = ("http://", "https://"),
        *,
        retry: Retry | None = None,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ) -> None:
        for p in prefixes:
            self.mount(
                p,
                retry=retry or Retry(0),
                pool_connections=pool_connections,
                pool_maxsize=pool_maxsize,
            )
