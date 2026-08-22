from datetime import datetime
from typing import List
from bs4 import Tag

from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.DaySchedule import DaySchedule
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser
from classes.schedule_parser.ScheduleParserSite import ScheduleParserSite
from src_utils.base_utils.get_time_obj import get_time_obj
from src_utils.base_utils.months_obj import months_obj

class JubiUtils:
    @staticmethod
    def get_date(data: Tag) -> datetime | None:
        date_raw = data.find('div', class_='date')
        date_list = date_raw.string.lower().split(' ')
        if len(date_list) > 1:
            month = months_obj[date_list[1]]
            day = int(date_list[0])
            date_object = datetime(datetime.now().year, month, day)
            return date_object

        return None

    @staticmethod
    def get_time_list(data: Tag, date: datetime) -> List[datetime]:
        time_list = []
        time_section_raw = data.find('div', class_='time_cont')
        time_list_raw = time_section_raw.find_all('a')
        for time_raw in time_list_raw:
            time_obj = get_time_obj(time_raw.string, date)
            if time_obj is not None:
                time_list.append(time_obj)
        return time_list

class JubiParser(ScheduleParserSite):
    url = 'https://www.yubi.ru/afisha/katok/'

    def __init__(self, utils = JubiUtils) -> None:
        self.utils = utils

    def get_day_schedule_list(self) -> List[DaySchedule]:
        soup = self._get_soup()
        data_list = soup.find_all('div', class_='skat_item_cont')
        return [
            schedule
            for data in data_list
            if (schedule := self._build_day_schedule(data)) is not None
        ]

    def _build_day_schedule(self, data: Tag) -> DaySchedule | None:
        date_obj = self.utils.get_date(data)
        if date_obj is None:
            return None
        time_list = self.utils.get_time_list(data, date_obj)
        return DaySchedule(date_obj, time_list)

def create_jubi_location_parser() -> LocationParser:
    return LocationParser(
        location_id=LocationId.JUBI,
        arena_name=ArenaName.JUBI,
        arena_id=ArenaId.JUBI_BASE,
        parser=JubiParser(JubiUtils),
    )

