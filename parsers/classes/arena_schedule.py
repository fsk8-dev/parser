from typing import List
from .session import Session
from .day_schedule import DaySchedule
from .arena_name import Arena
from .arena_id import ArenaId
from .schedule_type import ScheduleType


class ArenaSchedule:
    """
    Represents a schedule for an arena.

    Args:
        arena_name (Arena): The name of the arena.
        arena_id (ArenaId): The ID of the arena.
        schedule_type_id (ScheduleType): The ID of the schedule type.
        arena_schedule (List[DaySchedule]): The schedule for the arena.
    """

    def __init__(self, arena_name: Arena, arena_id: ArenaId, schedule_type_id: ScheduleType, arena_schedule: List[DaySchedule]):
        # Assign the provided arena name, ID, and schedule type ID to the instance variables
        self.arena_name = arena_name
        self.arena_schedule = arena_schedule
        self.arenaId = arena_id
        self.scheduleTypeId = schedule_type_id
        self.sessionList = []
        self.create_session_list()

    def create_session_list(self):
        for day_schedule in self.arena_schedule:
            for time in day_schedule.day_time_list:
                self.sessionList.append(Session(time))

