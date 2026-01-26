from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from ..classes.day_schedule import DaySchedule
from ..classes.arena_schedule import ArenaSchedule


class LocationParser(ABC):
    """
    Абстрактный базовый класс для парсеров расписания катков.
    Каждый конкретный парсер должен реализовать все абстрактные методы.
    """

    @abstractmethod
    def get_time_list(self, *args, **kwargs) -> List[datetime]:
        """
        Получить список временных слотов для занятий.

        Returns:
            List[datetime]: Список объектов datetime, представляющих временные слоты
        """
        pass

    @abstractmethod
    def get_day_schedule_list(self, *args, **kwargs) -> List[DaySchedule]:
        """
        Получить расписание на день.

        Returns:
            List[DaySchedule]: Список объектов DaySchedule с расписанием на день
        """
        pass

    @abstractmethod
    def get_arena_schedule_list(self, *args, **kwargs) -> List[ArenaSchedule]:
        """
        Получить расписание для арены.

        Returns:
            List[ArenaSchedule]: Список объектов ArenaSchedule с расписанием арены
        """
        pass

    @abstractmethod
    def get_date(self, *args, **kwargs) -> Optional[datetime]:
        """
        Получить дату из строки или объекта.

        Returns:
            Optional[datetime]: Объект datetime с датой или None, если не удалось распознать
        """
        pass

    @abstractmethod
    def get_date_list(self, *args, **kwargs) -> List[datetime]:
        """
        Получить список дат за указанный период.

        Returns:
            List[datetime]: Список объектов datetime за указанный период
        """
        pass

    @abstractmethod
    def get_schedule(self) -> List[ArenaSchedule]:
        """
        Основной метод для получения расписания.

        Returns:
            List[ArenaSchedule]: Список объектов ArenaSchedule с расписанием
        """
        pass


