from managers import SessionManager
from configs import CacheConfig, ConfigBox
from exceptions import CacheDisabledError
from type_defs import CachedSession, NotCachedSession


class CacheController:
    def __init__(self,
                 session_manager: SessionManager,
                 configs: ConfigBox) -> None:
        self._session_manager = session_manager
        self._configs = configs

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


