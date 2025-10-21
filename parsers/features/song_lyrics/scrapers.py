from bs4 import BeautifulSoup
from furl import furl

from ..base_scraper import BaseScraper
from .dtos import SongInfoDTO, SongLyricsDTO
from .endpoints import get_search_texts_url, get_text_url
from .exceptions import TextNotFoundError


class SearchSongsScraper(BaseScraper[list[SongInfoDTO]]):
    def __call__(self, search_str: str) -> list[SongInfoDTO]:
        """
        Retrieve search results for music texts matching the given query.

        Sends a GET request to the text search endpoint, parses the resulting HTML page,
        and extracts all found text titles along with their corresponding URLs.

        :param search_str:
            The search query string (e.g., a song title or artist name).
        :return:
            A list of `SongInfoDTO` instances, where each element contains:
              - `name`: The displayed title of the found text.
              - `slug`: The slug to the full text page.
        :raises ScrapingError:
            If a network or parsing error occurs during the request.
        """
        resp = self._client.request(method="get", url=get_search_texts_url(search_str))
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        search_results = soup.find_all("ul", class_="search-results-list")
        text_infos = []
        for result in search_results:
            for tag in result.find_all("a"):
                name = tag.text
                slug = furl(tag.get("href").rstrip("/")).path.segments[-1]
                text_infos.append(SongInfoDTO(name, slug))
        return text_infos


class SongLyricsScraper(BaseScraper[SongLyricsDTO]):
    def __call__(self, slug: str) -> SongLyricsDTO:
        """
        Retrieve song lyrics and optional translation by slug.

        Sends a GET request to the lyrics page, parses HTML, and extracts
        text from <div class="song_text"> and <div class="trans_text"> blocks.
        Removes captions like "Текст песни" and "Перевод на русский".

        :param slug: The last path segment of the song URL.
        :return: A `SongLyricsDTO` with lyrics text and optional translation.
        :raises TextNotFoundError: If lyrics or page are not found.
        :raises ScrapingError: On network or parsing errors.
        """
        resp = self._client.request(method="get", url=get_text_url(slug))
        if resp.status_code == 404:
            raise TextNotFoundError(f"No song lyrics found for this slug: {slug!r}")
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        song_text = soup.find("div", class_="song_text")
        trans_text = soup.find("div", class_="trans_text")

        song_text = song_text.text.strip().removeprefix("Текст песни").strip()
        if trans_text:
            trans_text = trans_text.text.strip().removeprefix("Перевод на русский").strip()

        return SongLyricsDTO(text=song_text, trans=trans_text)
