from typing import Union, Optional, Mapping, Callable
from requests_cache import CachedSession
from requests import Session as NotCachedSession, Request, PreparedRequest, Response
from requests.adapters import HTTPAdapter
from configs import ConfigBox, ClientConfig, CacheConfig
from urllib3.util.retry import Retry
from type_defs import ProxyLike, SessionLike
from exceptions import SwitchSessionError


class SessionFactory:
    @staticmethod
    def create(client_config: ClientConfig, cache_config: CacheConfig) -> SessionLike:
        if cache_config.enabled:
            return CachedSession(
                cache_name=cache_config.name or client_config.name,
                backend=cache_config.backend,
                expire_after=cache_config.ttl,
                cache_control=cache_config.cache_control
            )
        return NotCachedSession()


class SessionManager:
    def __init__(self,
                 configs: ConfigBox
                 ) -> None:
        self._configs = configs
        self.session: Optional[SessionLike] = SessionFactory.create(configs.client, configs.cache)

    # ---------- lifecycle ----------
    def close(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None

    def __enter__(self) -> "SessionManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def switch_cache(self, new_cache_config: CacheConfig) -> None:
        old = self.session
        try:
            new = SessionFactory.create(self._configs.client, new_cache_config)
            new.headers.update(old.headers)
            new.proxies.update(old.proxies)
            new.cookies.update(old.cookies)
            new.adapters.update(old.adapters)
            self.session.close()
            self.session = new
        except Exception as err:
            self.session = old
            raise SwitchSessionError("A session change error occurred during a cache change") from err



    # ---------- proxies utils ----------
    @staticmethod
    def _normalize_proxy(p: ProxyLike) -> ProxyLike:
        if p is None:
            return None
        if isinstance(p, str):
            return {"http": p, "https": p}
        return dict(p)

    @classmethod
    def _select_proxies(cls, call_proxies: ProxyLike, strat_proxies: ProxyLike) -> ProxyLike:
        call = cls._normalize_proxy(call_proxies)
        strat = cls._normalize_proxy(strat_proxies)
        if call is None:
            return strat
        if strat is None:
            return call
        merged = dict(strat)
        merged.update(call)
        return merged

    # ---------- request path ----------
    def prepare(self, method: str, url: str, **kwargs) -> PreparedRequest:
        """Use before send()"""
        req = Request(method=method, url=url, **kwargs)
        return self.session.prepare_request(req)

    def send(self,
             request: PreparedRequest,
             timeout: int | float | None = None,
             proxies: str | Mapping[str, str] | None = None,
             **kwargs) -> Response:
        strat_proxies = None
        if callable(self._configs.net.proxy_strategy):
            strat_proxies = self._configs.net.proxy_strategy(request.url)
        return self.session.send(request,
                                 timeout=timeout or self._configs.net.timeout,
                                 proxies=self._select_proxies(proxies, strat_proxies),
                                 **kwargs)
