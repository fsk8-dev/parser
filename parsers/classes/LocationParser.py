from abc import \
    ABC, \
    abstractmethod
from typing import \
    Dict, \
    Any, \
    Optional, \
    List, Protocol
import \
    logging
from datetime import \
    datetime

from .ArenaId import ArenaId
from .ArenaName import ArenaName
from .LocationId import LocationId
from .ScheduleType import ScheduleType
from ..classes.DaySchedule import DaySchedule
from ..classes.ArenaSchedule import ArenaSchedule


class ScheduleParser(Protocol):
    """Источник расписания. Первая реализация — подклассы ScheduleParserSite."""
    def get_day_schedule_list(self) -> List[DaySchedule]:
        ...

class LocationParser:
    """
    Идентификатор отдельной локации.
    Хранит LocationId / ArenaName / ArenaId / ScheduleType и делегирует
    разбор источника переданному parser (композиция).
    """

    def __init__(
        self,
        *,
        location_id: LocationId,
        arena_name: ArenaName,
        arena_id: ArenaId,
        parser: ScheduleParser,
        schedule_type: ScheduleType = ScheduleType.ICE_SKATING,
    ) -> None:
        self.location_id = location_id
        self.arena_name = arena_name
        self.arena_id = arena_id
        self.schedule_type = schedule_type
        self.parser = parser


    def get_schedule(self) -> List[ArenaSchedule]:
        day_schedule_list = self.parser.get_day_schedule_list()
        arena_schedule = ArenaSchedule(
            self.location_id,
            self.arena_name,
            self.arena_id,
            self.schedule_type,
            day_schedule_list,
        )
        return [arena_schedule]
