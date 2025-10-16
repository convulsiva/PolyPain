from furl import furl
from infra.client import configs as cfgs

from . import dtos, exceptions
from .parser import ScheduleParser

schedule_parser = ScheduleParser(
    cfgs.ConfigBox(
        client=cfgs.ClientConfig(furl("https://ruz.spbstu.ru/"), "RuzSPbPU"),
        net=cfgs.NetConfig(),
        cache=cfgs.CacheConfig(enabled=True, automatic_prune_cache=True, ttl=10),
        cookie=cfgs.CookieConfig(),
    )
)

__all__ = ["schedule_parser", "exceptions", "dtos"]
