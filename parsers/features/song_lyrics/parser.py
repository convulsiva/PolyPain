from ...infra.client import configs
from ..base_parser import BaseParser
from .scrapers import SearchSongsScraper, SongLyricsScraper


class SongLyricsParser(BaseParser):
    def __init__(self, config_box: configs.ConfigBox) -> None:
        super().__init__(config_box)
        self.search_songs = SearchSongsScraper(self._client)
        self.get_song_lyrics = SongLyricsScraper(self._client)
