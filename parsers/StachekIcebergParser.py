import re
from datetime import datetime
from typing import List

from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.DaySchedule import DaySchedule
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser
from classes.schedule_parser.VKScheduleParser import VKScheduleParser
from src_utils.DateTimeCustomUtils import DateTimeCustomUtils
from src_utils.base_utils.get_time_obj import get_time_obj


class StachekIcebergUtils:
    """
    Вспомогательные методы разбора текста поста расписания катка
    «Айсберг Арена».

    Расписание в очищенном тексте поста представлено блоками вида
    ``«<дата>\\nмассовоекатание\\n<интервалы HH:MM-HH:MM>»``.
    """

    TIME_PATTERN = r'\d{1,2}:\d{2}-\d{1,2}:\d{2}'
    """Шаблон строки интервала времени сеанса."""

    @staticmethod
    def get_date(match: tuple) -> datetime:
        """
        Извлекает дату дня из совпадения шаблона расписания.

        Группа 1 совпадения содержит день и месяц вида ``«17.08»``;
        год берётся текущий.

        :param match: кортеж групп совпадения SKATING_SCHEDULE_PATTERN.
        :type match: tuple
        :return: дата дня расписания.
        :rtype: datetime
        """
        return datetime.strptime(f'{match[0]}.{datetime.now().year}', '%d.%m.%Y')

    @staticmethod
    def get_sessions(time_list_raw: List[str], date: datetime) -> List[datetime]:
        """
        Извлекает список времён сеансов из строк интервалов.

        Строки, не соответствующие шаблону :attr:`TIME_PATTERN`,
        пропускаются. Значения, которые ``get_time_obj`` не смог
        разобрать (None), в результат не включаются.

        :param time_list_raw: строки блока времён сеансов.
        :type time_list_raw: List[str]
        :param date: дата, к которой привязываются времена сеансов.
        :type date: datetime
        :return: список времён начала сеансов.
        :rtype: List[datetime]
        """
        time_list = []
        for time in time_list_raw:
            if re.search(StachekIcebergUtils.TIME_PATTERN, time):
                time_obj = DateTimeCustomUtils.parse_hour_minute(time.split('-')[0], date)
                if time_obj is not None:
                    time_list.append(time_obj)
        return time_list


class StachekIcebergParser(VKScheduleParser):
    """
    Парсер расписания катка «Айсберг Арена».

    Выбирает актуальный пост сообщества :attr:`url` по шаблону
    :attr:`PERIOD_PATTERN` и формирует список расписаний по дням
    из блоков массового катания.
    """

    url = 'icebergkatok'
    """screen_name сообщества ВКонтакте катка."""

    PERIOD_PATTERN = r'расписание.*?((\d{2}\.\d{2}).*?(\d{2}\.\d{2})).*(?=\n)'
    """Шаблон строки периода расписания в очищенном тексте поста."""

    SKATING_SCHEDULE_PATTERN = r'(\d{1,2}\.\d{1,2}).*\nмассовоекатание.*\n((\d{1,2}:\d{1,2}-\d{1,2}:\d{1,2}\n){0,})'
    """Шаблон блока массового катания в очищенном тексте поста."""

    def __init__(self, utils: StachekIcebergUtils, token: str | None = None) -> None:
        """
        :param utils: класс или объект со вспомогательными методами разбора
                      текста поста (по умолчанию StachekIcebergUtils).
        :type utils: StachekIcebergUtils
        :param token: токен доступа VK API (см. VKScheduleParser).
        :type token: str | None
        """
        super().__init__(token=token)
        self.utils = utils

    def get_day_schedule_list(self) -> List[DaySchedule]:
        """
        Возвращает список расписаний по дням из актуального поста.

        Если актуальный пост не найден, возвращается пустой список —
        LocationParser при этом всё равно создаст ArenaSchedule
        с пустым sessionList.

        :return: список объектов DaySchedule.
        :rtype: List[DaySchedule]
        """
        posts = self._get_posts_with_schedule(self.PERIOD_PATTERN)
        result = []
        for post in posts:
            for match in re.findall(self.SKATING_SCHEDULE_PATTERN, post):
                date = self.utils.get_date(match)
                sessions = self.utils.get_sessions(match[1].split('\n'), date)
                result.append(DaySchedule(date, sessions))
        return result


def create_stachek_iceberg_location_parser() -> LocationParser:
    """
    Создаёт LocationParser для катка «Айсберг Арена».

    :return: сконфигурированный LocationParser с StachekIcebergParser внутри.
    :rtype: LocationParser
    """
    return LocationParser(
        location_id=LocationId.STACHEK_ICEBERG,
        arena_name=ArenaName.STACHEK_ICEBERG,
        arena_id=ArenaId.STACHEK_ICEBERG,
        parser=StachekIcebergParser(StachekIcebergUtils()),
    )
