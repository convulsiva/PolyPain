from furl import furl
from infra.client import configs as cfgs

from . import dtos, exceptions
from .parser import SongLyricsParser

song_lyrics_parser = SongLyricsParser(
    cfgs.ConfigBox(
        client=cfgs.ClientConfig(furl("delete from here"), "SongLyrics"),
        net=cfgs.NetConfig(),
        cache=cfgs.CacheConfig(
            enabled=True,
            ttl=-1,  # Immortal cache
            name="song_lyrics_parser_cache.sqlite",
        ),
        cookie=cfgs.CookieConfig(),
    )
)

__all__ = ["song_lyrics_parser", "exceptions", "dtos"]
