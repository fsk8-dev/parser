from abc import ABC, abstractmethod
from typing import Literal
from bs4 import BeautifulSoup

import requests
from .BaseScheduleParser import BaseScheduleParser


def _get_soup(response_data: str | bytes, parser_type: Literal['lxml', 'html.parser'] = 'lxml'):
    return BeautifulSoup(response_data, parser_type)


class ScheduleParserSite(BaseScheduleParser, ABC):
    pass

    @property
    def url(self) -> str:
        pass

    def _get_response(self):
        return requests.get(self.url)






