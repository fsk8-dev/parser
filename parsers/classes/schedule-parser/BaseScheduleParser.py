from abc import ABC, abstractmethod


class BaseScheduleParser(ABC):

    @abstractmethod
    def get_schedule(self):
        pass

    @abstractmethod
    def _get_arena_schedule(self):
        pass

    @abstractmethod
    def _get_day_schedule_list(self):
        pass
