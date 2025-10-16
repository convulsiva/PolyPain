from furl import furl
from infra.client import configs

SCHEDULE_CONFIG = configs.ConfigBox(
    client=configs.ClientConfig(furl("https://ruz.spbstu.ru/"), "RuzSPbPU"),
    net=configs.NetConfig(),
    cache=configs.CacheConfig(enabled=True, automatic_prune_cache=True, ttl=10),
    cookie=configs.CookieConfig(),
)
