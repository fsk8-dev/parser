from abc import ABC, abstractmethod
from typing import Literal, List
from bs4 import BeautifulSoup

import requests
from .BaseScheduleParser import BaseScheduleParser
from ..DaySchedule import DaySchedule


# todo добавить в зависимости BaseScheduleParserUtils
# todo сделать метод _build_day_schedule в нем вызывать
#  - utils.self.utils.get_date(day) и
#  - utils.get_time_list(sessions, day_date)

class SiteScheduleParser(BaseScheduleParser, ABC):
    """
    Абстрактный базовый класс парсера расписания, получающего данные с сайта.

    Инкапсулирует загрузку HTML-страницы по адресу :attr:`url` и её разбор
    через BeautifulSoup. Наследникам достаточно переопределить :attr:`url`
    и реализовать :meth:`get_day_schedule_list`.
    """

    parser_type: Literal['lxml', 'html.parser'] = 'lxml'
    """Тип парсера BeautifulSoup, используемого для разбора HTML."""

    @abstractmethod
    def get_day_schedule_list(self) -> List[DaySchedule]:
        """
        Возвращает список расписаний по дням, полученный с сайта.

        :return: список объектов DaySchedule, каждый из которых содержит
                 дату дня (day_date) и список времён сеансов (day_time_list).
        :rtype: List[DaySchedule]
        """
        ...

    def _get_response(self) -> requests.Response:
        """
        Выполняет HTTP GET-запрос по адресу :attr:`url`.

        :return: ответ сервера.
        :rtype: requests.Response
        """
        return requests.get(self.url)

    def _get_response_data(self, response: requests.Response) -> str | bytes:
        """
        Извлекает тело ответа для дальнейшего разбора.

        :param response: ответ сервера на запрос страницы расписания.
        :type response: requests.Response
        :return: текстовое содержимое ответа.
        :rtype: str | bytes
        """
        return response.text

    def _get_soup(self) -> BeautifulSoup:
        """
        Загружает страницу расписания и возвращает объект BeautifulSoup.

        :return: объект BeautifulSoup, построенный по содержимому страницы
                 с использованием парсера :attr:`parser_type`.
        :rtype: BeautifulSoup
        """
        response = self._get_response()
        return BeautifulSoup(self._get_response_data(response), self.parser_type)

