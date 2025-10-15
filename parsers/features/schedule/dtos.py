from dataclasses import dataclass
import datetime
from enum import IntEnum


@dataclass(frozen=True, slots=True)
class WeekDTO:
    date_start: datetime.date
    date_end: datetime.date
    is_odd: bool


class WeekParity(IntEnum):
    EVERY = 0
    EVEN = 1
    ODD = 2


@dataclass(frozen=True, slots=True)
class FacultyDTO:
    id_: int  # Какой-то внутренний id
    name: str  # Полное название: институт компьютерных наук и кибербезопасности
    abbr: str  # например ИКНК


@dataclass(frozen=True, slots=True)
class GroupDTO:
    id_: int  # Внутренний id, через него поиск расписания по группе
    name: str  # Публичное имя, 5130902/40003
    level: int  # Курс, первый курс, второй и тд... от 1 и до 5
    faculty: FacultyDTO


@dataclass(frozen=True, slots=True)
class TeacherDTO:
    id_: int  # Используется в запросах по расписанию преподавателя
    oid_: int  # Какой-то внешний id из корп. базы СПбПУ
    full_name: str  # Полное имя, например Ульянова Нина Сергеевна
    chair: str  # название кафедры, например 50/05 Кафедра "Высшая математика"


@dataclass(frozen=True, slots=True)
class BuildingDTO:
    id_: int  # Внутренний id, быть может, существует расписание по корпусу?
    name: str  # 3-й учебный корпус - полное название корпуса
    abbr: str  # сокращённое название, например: 3 к.
    address: str  # Возможный адрес? почти всегда пустой(


@dataclass(frozen=True, slots=True)
class AuditoryDTO:
    id_: int  # Внутренний id, через него можно получить расписание по аудитории
    name: str  # Название аудитории, например 404а или 505, 201 итд
    building: BuildingDTO  # Корпус


@dataclass(frozen=True, slots=True)
class LessonDTO:
    name: str  # название пары
    type_: str
    additional_info: str  # Доп информация о паре, зачастую пустая
    time_start: datetime.time
    time_end: datetime.time
    parity: WeekParity  # по каким неделям предмет, по чётным или нечётным, или каждую неделю
    groups: list[GroupDTO]
    teachers: list[TeacherDTO]
    auditories: list[AuditoryDTO]
    webinar_url: str  # может поменять на furl
    lms_url: str  # может поменять на furl


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
    weekday: WeekDay  # номер дня в неделе от 1 до 6
    date: datetime.date
    lessons: list[LessonDTO]


@dataclass(frozen=True, slots=True)
class WeekScheduleDTO:
    week: WeekDTO
    days: list[DayDTO]
    group: GroupDTO
