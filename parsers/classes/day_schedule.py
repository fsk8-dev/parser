from typing import List
from datetime import datetime


class DaySchedule:
    def __init__(self, day_date: datetime, day_time_list: List[datetime]):
        self.day_date = day_date
        self.day_time_list = day_time_list

