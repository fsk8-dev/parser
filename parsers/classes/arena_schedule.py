from typing import List
from .day_schedule import DaySchedule
from .arena_name import Arena


class ArenaSchedule:
    """
    Represents a schedule for an arena.

    Attributes:
        arena_name (Arena): The name of the arena.
        arena_schedule (List[DaySchedule]): The schedule for the arena.
    """

    def __init__(self, arena_name: Arena, arena_schedule: List[DaySchedule]):
        """
        Initializes an ArenaSchedule object.

        Args:
            arena_name (Arena): The name of the arena.
            arena_schedule (List[DaySchedule]): The schedule for the arena.
        """
        # Assign the provided arena name to the instance variable
        self.arena_name = arena_name

        # Assign the provided arena schedule to the instance variable
        self.arena_schedule = arena_schedule
