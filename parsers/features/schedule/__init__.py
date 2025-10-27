from ...infra.client import configs as cfgs
from . import dtos, exceptions
from .parser import ScheduleParser

schedule_parser = ScheduleParser(
    cfgs.ConfigBox(
        net=cfgs.NetConfig(),
        cache=cfgs.CacheConfig(
            enabled=True,
            automatic_prune_cache=True,
            prune_interval=10 * 60,
            ttl=30 * 60,  # time in seconds
            name="schedule_parser_cache.sqlite",
        ),
        cookie=cfgs.CookieConfig(),
    )
)

__all__ = ["schedule_parser", "exceptions", "dtos"]
