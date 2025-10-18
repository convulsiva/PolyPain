from time import time as get_seconds_now

from fake_useragent import UserAgent
from requests import PreparedRequest, Response

from .configs import ConfigBox
from .controllers import (
    AdaptersController,
    CacheController,
    CookiesController,
    HeadersController,
    ProxiesController,
)
from .managers import SessionManager
from .type_defs import ProxyLike, SessionLike


class Client:
    def __init__(self, configs: ConfigBox) -> None:
        self._time_last_cache_prune: float = float("-inf")
        self._configs = configs
        self._session_manager = SessionManager(configs)

        self._cache = CacheController(self._session_manager, self._configs)
        self._cookies = CookiesController(self._session_manager, self._configs)
        self._headers = HeadersController(self._session_manager, self._configs)
        self._proxies = ProxiesController(self._session_manager, self._configs)
        self._adapters = AdaptersController(self._session_manager, self._configs)

        self._bootstrap()  # Setting a retray policy + cookies + headers (+ user agent)

    def _bootstrap(self) -> None:
        self._cookies.update(self._configs.cookie.initial)
        self._cookies.update(self._configs.cookie.file)
        self._adapters.mount("http://", retry=self._configs.net.retry)
        self._adapters.mount("https://", retry=self._configs.net.retry)
        headers = dict(self._configs.net.headers)
        headers.setdefault("User-Agent", self._configs.net.user_agent or UserAgent().random)
        self._headers.update(headers)

    @property
    def session(self) -> SessionLike:
        return self._session_manager.session

    @property
    def cache(self) -> CacheController:
        return self._cache

    @property
    def cookies(self) -> CookiesController:
        return self._cookies

    @property
    def headers(self) -> HeadersController:
        return self._headers

    @property
    def proxies(self) -> ProxiesController:
        return self._proxies

    @property
    def adapters(self) -> AdaptersController:
        return self._adapters

    def _prune_cache_via_ttl(self) -> None:
        if not self._configs.cache.enabled:
            return
        if self._configs.cache.ttl < 0:
            return
        time_now = get_seconds_now()
        if time_now - self._time_last_cache_prune >= self._configs.cache.prune_interval:
            self._cache.prune()
            self._time_last_cache_prune = time_now

    def request(
        self,
        method: str,
        url: str,
        *,
        timeout: int | float | None = None,
        proxies: ProxyLike = None,
        prepare_kwargs: dict | None = None,
        **send_kwargs,
    ) -> Response:
        """
        A single entry point: prepares a PreparedRequest and sends it through the SessionManager.
        – method, url: same as in requests
        – timeout: overrides NetConfig.timeout for a single call
        – proxies: overrides the strategy/values for a single call (str | mapping | None)
        – prepare_kwargs: everything passed to Request(...): params / data / json / files /
                                                             headers / cookies / auth, etc.
        – send_kwargs: everything passed to session.send(): stream, allow_redirects, etc.
        """
        if self._configs.cache.automatic_prune_cache:
            self._prune_cache_via_ttl()
        req: PreparedRequest = self._session_manager.prepare(
            method=method, url=url, **(prepare_kwargs or {})
        )
        resp: Response = self._session_manager.send(
            request=req, timeout=timeout, proxies=proxies, **send_kwargs
        )
        return resp

    def close(self) -> None:
        self.cache.prune()
        self.session.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        cache_config = self._configs.cache
        ttl = "immortal" if cache_config.ttl < 0 else cache_config.ttl
        return (
            f"<{self.__class__.__name__} name={self._configs.client.name!r} "
            f"cache={'on' if cache_config.enabled else 'off'} ttl={ttl} "
            f"base_url={self._configs.client.base_url}>"
        )
