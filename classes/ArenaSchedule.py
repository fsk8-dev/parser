from typing import List
from .Session import Session
from .DaySchedule import DaySchedule
from .LocationId import LocationId
from .ArenaName import ArenaName
from .ArenaId import ArenaId
from .ScheduleType import ScheduleType


class ArenaSchedule:
    """
    Initialize the ArenaSchedule object with the provided parameters.

    Args:
        location_id (LocationId): The ID of the location.
        arena_name (ArenaName): The name of the arena.
        arena_id (ArenaId): The ID of the arena.
        schedule_type_id (ScheduleType): The ID of the schedule type.
        day_schedule_list (List[DaySchedule]): List of day schedules for the arena.
    """

    def __init__(self, location_id: LocationId, arena_name: ArenaName, arena_id: ArenaId, schedule_type_id: ScheduleType, day_schedule_list: List[DaySchedule]):
        # Assign the provided arena name, ID, and schedule type ID to the instance variables
        self.locationId = location_id.value
        self.arenaName = arena_name.value
        self.arenaId = arena_id.value
        self.scheduleTypeId = schedule_type_id.value
        self.sessionList = []
        self.create_session_list(day_schedule_list)

    def create_session_list(self, day_schedule_list):
        for day_schedule in day_schedule_list:
            for time in day_schedule.day_time_list:
                self.sessionList.append(Session(time))

