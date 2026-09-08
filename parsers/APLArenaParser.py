import re
from typing import List

from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.DaySchedule import DaySchedule
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser
from classes.schedule_parser.VKScheduleParser import VKScheduleParser


class APLAUtils:
    @staticmethod
    def get_sessions():
        pass


class APLArenaParser(VKScheduleParser):
    url = '238896923'
    PERIOD_PATTERN = ''
    SCHEDULE_TITLE = 'расписаниемассовыхкатаний'
    SKATING_SCHEDULE_PATTERN = ''

    def __init__(self, utils: APLAUtils, token: str | None = None) -> None:
        """
        :param utils: класс или объект со вспомогательными методами разбора
                      текста поста (по умолчанию APLAUtils).
        :type utils: APLAUtils
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
        posts = self._get_posts_with_schedule(self.SCHEDULE_TITLE)
        result = []
        for post in posts:
            for match in re.findall(self.SCHEDULE_TITLE, post):
                print(match)
        return result


def create_apla_location_parser() -> LocationParser:
    """
    Создаёт LocationParser для катка «Центр спорта " АПЛ арена"».

    :return: сконфигурированный LocationParser с APLArenaParser внутри.
    :rtype: LocationParser
    """
    return LocationParser(
        location_id=LocationId.APLA,
        arena_name=ArenaName.APLA,
        arena_id=ArenaId.APLA,
        parser=APLArenaParser(APLAUtils()),
    )
