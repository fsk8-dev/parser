from typing import List
from .day_schedule import DaySchedule


class ArenaSchedule:

    def __init__(self, arena_name: str, arena_schedule: List[DaySchedule]):
        self.arena_name = arena_name
        self.arena_schedule = arena_schedule
