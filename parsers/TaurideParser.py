from datetime import datetime
from typing import List
import json
import re


from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.DaySchedule import DaySchedule
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser

from classes.schedule_parser.SiteScheduleParser import SiteScheduleParser
from src_utils.base_utils.get_time_obj import get_time_obj


class TaurideUtils:
    """
    Вспомогательные методы для разбора расписания катка «Таврический сад».

    Расписание на сайте формируется JavaScript'ом: данные хранятся в теге
    ``<script>`` в виде объекта ``scheduleData`` с массивами заголовков
    колонок (дни) и ячеек (сеансы).
    """

    @staticmethod
    def get_schedule_data(soup) -> dict:
        """
        Извлекает данные расписания из JavaScript-объекта ``scheduleData``.

        Находит тег ``<script>``, содержащий объявление ``let scheduleData``,
        и извлекает из него массивы ``columnHeaders`` (заголовки дней)
        и ``cells`` (ячейки сеансов).

        :param soup: объект BeautifulSoup загруженной страницы расписания.
        :type soup: BeautifulSoup
        :return: словарь с ключами ``headers`` (список заголовков дней)
                 и ``cells`` (список ячеек сеансов).
        :rtype: dict
        """
        script = soup.find('script', string=re.compile(r'let scheduleData'))
        text = script.get_text()
        return {
            'headers': json.loads(re.search(r'columnHeaders:\s*(\[.*?\])', text, re.S).group(1)),
            'cells': json.loads(re.search(r'cells:\s*(\[.*?\])', text, re.S).group(1)),
        }

    @staticmethod
    def get_date(header: str) -> datetime:
        """
        Разбирает заголовок колонки и возвращает дату дня.

        Ожидает строку вида ``"день недели<br>DD.MM"``. Год определяется
        относительно текущей даты: если месяц меньше текущего, берётся
        следующий год.

        :param header: заголовок колонки расписания, например ``"вс<br>17.08"``.
        :type header: str
        :return: дата дня расписания.
        :rtype: datetime
        """
        day, month = map(int, header.split('<br>')[1].split('.'))  # "17.08"
        year = datetime.now().year
        if month < datetime.now().month:
            year += 1
        return datetime(year, month, day)

    @staticmethod
    def get_time_list(cells, date) -> List[datetime]:
        """
        Извлекает отсортированный список времён начала сеансов из ячеек.

        Из подписи каждой ячейки вида ``"HH:MM-HH:MM"`` берётся время начала
        сеанса и привязывается к переданной дате. Ячейки, не прошедшие
        разбор, пропускаются.

        :param cells: список ячеек расписания (словарей с ключом ``label``).
        :type cells: list
        :param date: дата, к которой привязываются времена сеансов.
        :type date: datetime
        :return: отсортированный по возрастанию список времён начала сеансов.
        :rtype: list
        """
        time_list = []
        for cell in cells:
            start = cell['label'].split('-')[0]  # "08:15-09:15" -> "08:15"
            time_obj = get_time_obj(start, date)
            if time_obj is not None:
                time_list.append(time_obj)
        return sorted(time_list)

class TaurideParser(SiteScheduleParser):
    """
    Парсер расписания массовых катаний катка «Таврический сад».

    Загружает страницу :attr:`url`, извлекает данные из JavaScript-объекта
    ``scheduleData`` и формирует список расписаний по дням. Учитываются
    только ячейки со состоянием ``available``.
    """

    url = 'https://www.tavrsad.com/public-skating/'
    """Адрес страницы расписания массовых катаний."""

    parser_type = 'html.parser'
    """Тип парсера BeautifulSoup, используемого для разбора страницы."""

    def __init__(self, utils: TaurideUtils):
        """
        :param utils: вспомогательный объект с методами разбора данных расписания.
        :type utils: TaurideUtils
        """
        self.utils = utils

    def get_day_schedule_list(self) -> List[DaySchedule]:
        """
        Возвращает список расписаний по дням.

        Дни без доступных сеансов, а также дни, для которых не удалось
        построить расписание, в результат не включаются.

        :return: список объектов DaySchedule.
        :rtype: List[DaySchedule]
        """
        soup = self._get_soup()
        data = self.utils.get_schedule_data(soup)

        result = []
        for col, day in enumerate(data['headers']):
            sessions = [c for c in data['cells'] if c['col'] == col and c['state'] == 'available']
            if not sessions:
                continue
            schedule = self._build_day_schedule(day, sessions)
            if schedule:
                result.append(schedule)
        return result


    def _build_day_schedule(self, day: str, sessions: List[str]) -> DaySchedule | None:
        """
        Формирует расписание одного дня из заголовка колонки и списка сеансов.

        :param day: заголовок колонки расписания, например ``"вс<br>17.08"``.
        :type day: str
        :param sessions: список ячеек доступных сеансов этого дня.
        :type sessions: List[str]
        :return: объект DaySchedule либо None, если дату или времена
                 получить не удалось.
        :rtype: DaySchedule | None
        """
        day_date = self.utils.get_date(day)
        time_list = self.utils.get_time_list(sessions, day_date)
        if day_date and time_list:
            return DaySchedule(day_date, time_list)
        return None




def create_tauride_location_parser() -> LocationParser:
    """
    Создаёт LocationParser для катка «Таврический сад».

    :return: сконфигурированный LocationParser с TaurideParser внутри.
    :rtype: LocationParser
    """
    return LocationParser(
        location_id=LocationId.TAVR,
        arena_name=ArenaName.TAVR,
        arena_id=ArenaId.TAVR,
        parser=TaurideParser(TaurideUtils())
    )
