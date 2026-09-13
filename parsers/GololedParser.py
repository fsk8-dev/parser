from datetime import datetime
from typing import List

from bs4 import BeautifulSoup, ResultSet, Tag

from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.DaySchedule import DaySchedule
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser
from classes.schedule_parser.SiteScheduleParser import SiteScheduleParser
from src_utils.DateTimeCustomUtils import DateTimeCustomUtils


class GololedUtils:
    @staticmethod
    def get_day_nodes(soup: BeautifulSoup) -> ResultSet:
        schedule_node = soup.find('div', id='schedule_for_all_component')
        return schedule_node.find_all('div', class_='schedule_table_item')

    @staticmethod
    def get_session_nodes(node: Tag, activity_slag: str) -> ResultSet:
        return node.find_all(attrs={'data-activity_slug': activity_slag})

    @staticmethod
    def parse_session_date(string: str) -> datetime | None:
        splitted = string.split(' ')

        if len(splitted) != 3:
            return None

        day, month, time = splitted
        date = DateTimeCustomUtils.parse_day_month_genitive(f"{day} {month}")
        return DateTimeCustomUtils.parse_hour_minute(time, date)



class GololedParser(SiteScheduleParser):
    url = 'https://gololed.spb.ru/'
    activity_slag = 'massovoe_katanie'

    def __init__(self, utils: GololedUtils) -> None:
        """
        :param utils: класс или объект со вспомогательными методами разбора
                      расписания (по умолчанию GololedUtils).
        :type utils: GololedUtils
        """
        self.utils = utils

    def get_day_schedule_list(self) -> List[DaySchedule]:
        soup = self._get_soup()
        day_nodes = self.utils.get_day_nodes(soup)
        return [
            schedule
            for node in day_nodes
            if (schedule := self._build_day_schedule(node)) is not None
        ]

    def _build_day_schedule(self, node: Tag) -> DaySchedule | None:
        sessions = []
        session_nodes = self.utils.get_session_nodes(node, self.activity_slag)
        for node in session_nodes:
            date_str = node.get('data-start_date')
            session = self.utils.parse_session_date(date_str)
            if session is not None:
                sessions.append(session)
        if len(sessions) == 0:
            return None
        date = sessions[0].replace(hour=0, minute=0, second=0)
        return DaySchedule(date, sessions)


def create_gololed_location_parser() -> LocationParser:
    """
    Создаёт LocationParser для катка «Гололед».

    :return: сконфигурированный LocationParser с GololedParser внутри.
    :rtype: LocationParser
    """
    return LocationParser(
        location_id=LocationId.GOLOLED,
        arena_name=ArenaName.GOLOLED,
        arena_id=ArenaId.GOLOLED,
        parser=GololedParser(GololedUtils)
    )
