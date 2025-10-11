from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GroupIdDTO:
    external_id: str
    internal_id: int
