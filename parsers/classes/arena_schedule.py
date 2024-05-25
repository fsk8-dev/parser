from typing import List
from .day_schedule import DaySchedule


class ArenaSchedule:
    """
    Represents a schedule for an arena.

    Attributes:
        arena_name (str): The name of the arena.
        arena_schedule (List[DaySchedule]): The schedule for the arena.
    """

    def __init__(self, arena_name: str, arena_schedule: List[DaySchedule]):
        """
        Initializes an ArenaSchedule object.

        Args:
            arena_name (str): The name of the arena.
            arena_schedule (List[DaySchedule]): The schedule for the arena.
        """
        self.arena_name = arena_name
        self.arena_schedule = arena_schedule
