from datetime import datetime
from typing import List
import json

from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.DaySchedule import DaySchedule
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser
from classes.schedule_parser.SiteScheduleParser import SiteScheduleParser


class GrandCanyonParser(SiteScheduleParser):
    url = 'https://cp.grand-ice.ru/api/schedules'

    def get_day_schedule_list(self) -> List[DaySchedule]:
        response = self._get_response()
        result = []
        if response.ok == False:
            return []
        data_json = json.loads(response.text)
        schedules = data_json['data']['schedules']
        for item in schedules:
            result.append(self._build_day_schedule_list(item))

        return result

    def _build_day_schedule_list(self, item: List) -> DaySchedule:
        day_date = datetime.strptime(item['date'], '%Y-%m-%d')
        times = item['schedule_time']
        time_list = []

        for t in times:
            time = datetime.strptime(t['time_start'], '%H:%M:%S')
            time_list.append(datetime.combine(day_date.date(), time.time()))

        return DaySchedule(day_date, time_list)


def create_grand_canyon_location_parser() -> LocationParser:
    """
    Создаёт LocationParser для катка «Гранд Каньон».

    :return: сконфигурированный LocationParser с GrandCanyonParser внутри.
    :rtype: LocationParser
    """
    return LocationParser(
        location_id=LocationId.GRAND_KANON,
        arena_name=ArenaName.GRAND_KANON,
        arena_id=ArenaId.GRAND_KANON,
        parser=GrandCanyonParser()
    )
