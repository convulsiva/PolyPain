from dataclasses import dataclass
import datetime
from enum import IntEnum


@dataclass(frozen=True, slots=True)
class WeekDTO:
    date_start: datetime.date
    date_end: datetime.date
    is_odd: bool


class LessonType(IntEnum):
    PRACTICE = 1
    LECTURE = 2
    LAB = 3
    TEST = 4
    EXAM = 5


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
    subject: str  # название пары
    subject_short: str  # название пары сокращённое, но иногда то же, что и subject
    type_: LessonType
    additional_info: str  # Доп информация о паре, зачастую пустая
    time_start: datetime.time
    time_end: datetime.time
    parity: WeekParity  # по каким неделям предмет, по чётным или нечётным, или каждую неделю
    groups: list[GroupDTO]
    teachers: list[TeacherDTO]
    auditories: list[AuditoryDTO]
    webinar_url: str  # может поменять на furl
    lms_url: str  # может поменять на furl


@dataclass(frozen=True, slots=True)
class DayDTO:
    weekday: int  # номер дня в неделе от 1 до 6
    date: datetime.date
    lessons: list[LessonDTO]


# main объект - заполняется полностью при отправке запроса на получение расписания группы
@dataclass(frozen=True, slots=True)
class WeekScheduleDTO:
    week: WeekDTO
    days: list[DayDTO]
    group: GroupDTO
