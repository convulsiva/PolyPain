from ...infra.client import Client, configs
from .scrapers import SearchSongsScraper, SongLyricsScraper


class SongLyricsParser:
    def __init__(self, config_box: configs.ConfigBox) -> None:
        self._client = Client(config_box)
        self.get_song_info = SearchSongsScraper(self._client)
        self.get_song_lyrics = SongLyricsScraper(self._client)
