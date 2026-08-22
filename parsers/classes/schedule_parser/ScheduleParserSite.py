from abc import ABC, abstractmethod
from typing import Literal, List
from bs4 import BeautifulSoup

import requests
from .BaseScheduleParser import BaseScheduleParser
from ..DaySchedule import DaySchedule


class ScheduleParserSite(BaseScheduleParser, ABC):
    parser_type: Literal['lxml', 'html.parser'] = 'lxml'

    @property
    def url(self) -> str:
        ...

    @abstractmethod
    def get_day_schedule_list(self) -> List[DaySchedule]:
        ...

    def _get_response(self) -> requests.Response:
        return requests.get(self.url)

    def _get_response_data(self, response: requests.Response) -> str | bytes:
        return response.text

    def _get_soup(self) -> BeautifulSoup:
        response = self._get_response()
        return BeautifulSoup(self._get_response_data(response), self.parser_type)
