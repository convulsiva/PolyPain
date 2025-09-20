from managers import SessionManager
from configs import CacheConfig
from exceptions import CacheDisabledError


class CacheController:
    def __init__(self, session_manager: SessionManager) -> None:
        self._m = session_manager

    # Solve config desynchronization problem
    def enable(self, cache_config: CacheConfig) -> None:
        if not cache_config.enabled:
            raise CacheDisabledError("In CacheConfig, the enabled field is False")
        self._m.switch_cache(cache_config)


