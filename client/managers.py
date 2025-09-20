from typing import Union, Optional, Mapping, Callable
from requests_cache import CachedSession
from requests import Session as NotCachedSession, Request, PreparedRequest, Response
from requests.adapters import HTTPAdapter
from configs import ClientConfig, NetConfig, CacheConfig, CookieConfig
from urllib3.util.retry import Retry
from type_defs import ProxyLike, SessionLike


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
                 client_config: ClientConfig,
                 net_config: NetConfig,
                 cache_config: CacheConfig,
                 cookie_config: CookieConfig,
                 proxy_strategy: Callable[[str], ProxyLike]) -> None:
        self.client_config = client_config
        self.net_config = net_config
        self.cache_config = cache_config
        self.cookie_config = cookie_config
        self._proxy_strategy = proxy_strategy
        self.session: Optional[SessionLike] = SessionFactory.create(client_config, cache_config)

    # ---------- lifecycle ----------
    def close(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None

    def __enter__(self) -> "SessionManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # ---------- configuration ----------
    def switch_cache(self, new_cache_config: CacheConfig) -> None:
        self.session.close()
        self.session = SessionFactory.create(self.client_config, new_cache_config)
        self.cache_config = new_cache_config

    def apply_retry(self, retry: Retry) -> None:
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def apply_headers(self, headers: Mapping[str, str]) -> None:
        self.session.headers.update(headers)

    def set_proxy_strategy(self, strategy: Callable[[str], ProxyLike]) -> None:
        self._proxy_strategy = strategy

    # ---------- request path ----------
    def prepare(self, method: str, url: str, **kwargs) -> PreparedRequest:
        # Use before send()
        req = Request(method=method, url=url, **kwargs)
        return self.session.prepare_request(req)

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
        strat.update(call)
        return strat

    def send(self,
             request: PreparedRequest,
             timeout: Optional[int | float] = None,
             proxies: Optional[str, Mapping[str, str]] = None,
             **kwargs) -> Response:
        return self.session.send(request,
                                 timeout=timeout or self.net_config.timeout,
                                 proxies=self._select_proxies(proxies, self._proxy_strategy(request.url)),
                                 **kwargs)
