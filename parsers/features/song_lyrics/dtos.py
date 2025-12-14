from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SongInfoDTO:
    name: str
    slug: str


@dataclass(frozen=True, slots=True)
class SongLyricsDTO:
    text: str
    trans: str | None
