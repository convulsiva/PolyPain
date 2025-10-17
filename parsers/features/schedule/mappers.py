import datetime as dt

from .dtos import (
    AuditoryDTO,
    BuildingDTO,
    DayDTO,
    FacultyDTO,
    GroupDTO,
    LessonDTO,
    TeacherDTO,
    WeekDay,
    WeekDTO,
    WeekParity,
    WeekScheduleDTO,
)
from .exceptions import DateFormatError, TimeFormatError


def map_week_schedule(data: dict) -> WeekScheduleDTO:
    return WeekScheduleDTO(
        week=_map_week(data["week"]),
        days=[_map_day(d) for d in (data.get("days") or [])],
        group=_map_group(data["group"]),
    )


# --- utils ---
def parse_date(s: str) -> dt.date:
    date_formats = ("%Y-%m-%d", "%Y.%m.%d")
    last_err = None
    for fmt in date_formats:
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError as err:
            last_err = err
            continue
    raise DateFormatError(
        f"Wrong date-format for {s}. Use one of {date_formats} format"
    ) from last_err


def _parse_time(s: str) -> dt.time:
    time_format = "%H:%M"
    try:
        return dt.datetime.strptime(s, time_format).time()
    except ValueError as err:
        raise TimeFormatError(f"Wrong time-format for {s}. Use {time_format} format") from err


# --- internal mappers ---
def _map_faculty(data: dict) -> FacultyDTO:
    return FacultyDTO(id_=data["id"], name=data["name"], abbr=data["abbr"])


def _map_group(data: dict) -> GroupDTO:
    return GroupDTO(
        id_=data["id"],
        name=data["name"],
        level=data["level"],
        faculty=_map_faculty(data["faculty"]),
    )


def _map_teacher(data: dict) -> TeacherDTO:
    return TeacherDTO(
        id_=data["id"], oid_=data["oid"], full_name=data["full_name"], chair=data["chair"]
    )


def _map_building(data: dict) -> BuildingDTO:
    return BuildingDTO(
        id_=data["id"], name=data["name"], abbr=data["abbr"], address=data["address"]
    )


def _map_auditory(data: dict) -> AuditoryDTO:
    return AuditoryDTO(id_=data["id"], name=data["name"], building=_map_building(data["building"]))


def _map_lesson(data: dict) -> LessonDTO:
    return LessonDTO(
        name=data["subject"],
        type_=data["typeObj"]["name"],
        additional_info=data["additional_info"],
        time_start=_parse_time(data["time_start"]),
        time_end=_parse_time(data["time_end"]),
        parity=WeekParity(data["parity"]),
        groups=[_map_group(group) for group in (data.get("groups") or [])],
        teachers=[_map_teacher(teacher) for teacher in (data.get("teachers") or [])],
        auditories=[_map_auditory(auditory) for auditory in (data.get("auditories") or [])],
        webinar_url=data["webinar_url"],
        lms_url=data["lms_url"],
    )


def _map_day(data: dict) -> DayDTO:
    return DayDTO(
        weekday=WeekDay(data["weekday"]),
        date=parse_date(data["date"]),
        lessons=[_map_lesson(lesson) for lesson in (data.get("lessons") or [])],
    )


def _map_week(data: dict) -> WeekDTO:
    return WeekDTO(
        date_start=parse_date(data["date_start"]),
        date_end=parse_date(data["date_end"]),
        is_odd=data["is_odd"],
    )
