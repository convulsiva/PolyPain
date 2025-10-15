from dataclasses import dataclass
import datetime
from enum import IntEnum


@dataclass(frozen=True, slots=True)
class WeekDTO:
    date_start: datetime.date  # Week start date
    date_end: datetime.date  # Week end date
    is_odd: bool  # True if the week is odd


class WeekParity(IntEnum):
    EVERY = 0  # Every week
    EVEN = 1  # Even weeks
    ODD = 2  # Odd weeks


@dataclass(frozen=True, slots=True)
class FacultyDTO:
    id_: int  # Internal faculty ID
    name: str  # Full faculty name
    abbr: str  # Short name, e.g. IKNC


@dataclass(frozen=True, slots=True)
class GroupDTO:
    id_: int  # Internal group ID
    name: str  # Group name, e.g. 5130902/40003
    level: int  # Study level (year)
    faculty: FacultyDTO  # Related faculty info


@dataclass(frozen=True, slots=True)
class TeacherDTO:
    id_: int  # Internal teacher ID
    oid_: int  # External system ID
    full_name: str  # Full name, e.g. Nina S. Ulyanova
    chair: str  # Department or chair name


@dataclass(frozen=True, slots=True)
class BuildingDTO:
    id_: int  # Building ID
    name: str  # Full building name
    abbr: str  # Short name, e.g. "Main"
    address: str  # Address (usually empty)


@dataclass(frozen=True, slots=True)
class AuditoryDTO:
    id_: int  # Classroom ID
    name: str  # Room name or number
    building: BuildingDTO  # Related building info


@dataclass(frozen=True, slots=True)
class LessonDTO:
    name: str  # Lesson title
    type_: str  # Lesson type (lecture, lab, etc.)
    additional_info: str  # Optional extra info
    time_start: datetime.time  # Start time
    time_end: datetime.time  # End time
    parity: WeekParity  # Week parity rule
    groups: list[GroupDTO]  # Related groups
    teachers: list[TeacherDTO]  # Related teachers
    auditories: list[AuditoryDTO]  # Related rooms
    webinar_url: str  # Webinar link (optional)
    lms_url: str  # LMS course link (optional)


class WeekDay(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


@dataclass(frozen=True, slots=True)
class DayDTO:
    weekday: WeekDay  # Day of the week
    date: datetime.date  # Date of this day
    lessons: list[LessonDTO]  # List of lessons on that day


@dataclass(frozen=True, slots=True)
class WeekScheduleDTO:
    week: WeekDTO  # Week info
    days: list[DayDTO]  # Days within this week
    group: GroupDTO  # Group the schedule belongs to
