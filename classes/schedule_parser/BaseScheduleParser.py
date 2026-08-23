from abc import ABC, abstractmethod
from typing import List

from classes.DaySchedule import DaySchedule


class BaseScheduleParser(ABC):
    @property
    def url(self) -> str:
        """
        Адрес страницы.

        :return: URL страницы.
        :rtype: str
        """
        ...

    @abstractmethod
    def get_day_schedule_list(self) -> List[DaySchedule]:
        """
         Возвращает список расписаний по дням.
         :return: список объектов DaySchedule, каждый из которых содержит
                  дату дня (day_date) и список времён занятий (day_time_list).
         :rtype: List[DaySchedule]
         """
        pass
