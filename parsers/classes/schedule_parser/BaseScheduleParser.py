from abc import ABC, abstractmethod
from typing import List

from parsers.classes.DaySchedule import DaySchedule


class BaseScheduleParser(ABC):

    @abstractmethod
    def get_day_schedule_list(self) -> List[DaySchedule]:
        pass
