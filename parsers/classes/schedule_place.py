from typing import List, Literal
from datetime import datetime
from .day_schedule import DaySchedule


FIGURE_SKATING: Literal['figure_skating'] = 'figure_skating'
HOCKEY: Literal['hockey'] = 'hockey'


class Place:
    def __init__(self, name: str, address: str, phone_list: List[str]):
        self.name = name
        self.address = address
        self.phone = phone_list


class SchedulePeriod:
    def __init__(self,
                 beg_period_date: datetime,
                 end_period_date: datetime,
                 day_schedule_list: List[DaySchedule]):
        self.beg_period_date = beg_period_date
        self.end_period_date = end_period_date
        self.day_schedule_list = day_schedule_list


class IceRink:
    def __init__(self, name: str, schedule_period: SchedulePeriod):
        self.name = name
        self.schedule_period = schedule_period


class Schedule:
    def __init__(self, sport_type: Literal[FIGURE_SKATING, HOCKEY], ice_rink_list: List[IceRink]):
        self.sport_type = sport_type
        self.ice_rink_list = ice_rink_list


class SchedulePlace:
    def __init__(self,
                 place: Place,
                 beg_schedule_date: datetime,
                 end_schedule_date: datetime,
                 figure_skating: Schedule,
                 hockey: Schedule):
        self.beg_schedule_date = beg_schedule_date
        self.end_schedule_date = end_schedule_date
        self.place = place
        self.figure_skating = figure_skating
        self.hockey = hockey




