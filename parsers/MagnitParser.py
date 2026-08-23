from datetime import datetime
from typing import List

from bs4 import BeautifulSoup
from bs4  import  ResultSet, Tag

from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.DaySchedule import DaySchedule
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser
from classes.schedule_parser.SiteScheduleParser import SiteScheduleParser
from src_utils.DateTimeCustomUtils import DateTimeCustomUtils


class MagnitArenaUtils:
    @staticmethod
    def get_data_list(soup: BeautifulSoup, container_id: str) -> ResultSet | None:
        container = soup.find('div', id=container_id)
        if container is None:
            return None
        data = container.find_all('div', class_='t1118__wrapper')
        return data

    @staticmethod
    def get_day(data: Tag) -> datetime | None:
        raw = data.find('span', class_='t1118__title').text
        if raw:
            date = DateTimeCustomUtils.find_day_month_by_digits(raw)
            if date:
                return DateTimeCustomUtils.parse_day_month(date)
        return None

    @staticmethod
    def get_sessions(data: Tag, date: datetime) -> List[datetime]:
        result = []
        container = data.find('div', class_='t1118__descr')
        raw_sessions = container.find_all('li', attrs={'data-list': 'bullet'})
        if raw_sessions:
            for session in raw_sessions:
                time_str = session.get_text(strip=True).split('-')[0].strip()
                time = DateTimeCustomUtils.parse_hour_minute(time_str, date)
                if time is not None:
                    result.append(time)
        return result


class MagnitArenaParser(SiteScheduleParser):
    url = 'https://magnit-arena.ru/'

    def __init__(self, utils: MagnitArenaUtils, container_id: str) -> None:
        """
        :param utils: класс или объект со вспомогательными методами разбора
                      расписания
        :type utils: MagnitArenaUtils
        """
        self.utils = utils
        self.container_id = container_id

    def get_day_schedule_list(self) -> List[DaySchedule]:
        soup = self._get_soup()
        data_list = self.utils.get_data_list(soup, self.container_id)
        if data_list is None:
            return []

        result = []
        for data in data_list:
            day_schedule = self._build_day_schedule(data)
            if day_schedule:
                result.append(day_schedule)
        return result

    def _build_day_schedule(self, data: Tag) -> DaySchedule | None:
        day = self.utils.get_day(data)
        if day is None:
            return None
        sessions = self.utils.get_sessions(data, day)
        if len(sessions) == 0:
            return None
        return DaySchedule(day, sessions)


def create_magnit_arena_location_parser() -> LocationParser:
    """
    Создаёт LocationParser для «Магнит Арена».

    :return: сконфигурированный LocationParser с MagnitArenaUtils внутри.
    :rtype: LocationParser
    """
    return LocationParser(
        location_id=LocationId.MAGNIT,
        arena_name=ArenaName.MAGNIT,
        arena_id=ArenaId.MAGNIT,
        parser=MagnitArenaParser(
            MagnitArenaUtils(),
            'rec2031604551'
        )
    )
