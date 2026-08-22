from datetime import datetime
from typing import List
from bs4 import Tag

from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.DaySchedule import DaySchedule
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser
from classes.schedule_parser.ScheduleParserSite import ScheduleParserSite
from src_utils.base_utils.get_time_obj import get_time_obj
from src_utils.base_utils.months_obj import months_obj

class JubiUtils:
    """
    Вспомогательные методы для разбора расписания катка «Юбилейный».

    Расписание на сайте представлено HTML-блоками ``div.skat_item_cont``,
    содержащими дату (``div.date``) и времена сеансов (``div.time_cont``).
    """

    @staticmethod
    def get_date(data: Tag) -> datetime | None:
        """
        Извлекает дату дня из блока расписания.

        Ожидает внутри блока тег ``div.date`` со строкой вида
        ``"17 августа"``: название месяца переводится в номер через
        ``months_obj``, год берётся текущий.

        :param data: HTML-тег блока расписания одного дня.
        :type data: Tag
        :return: дата дня расписания либо None, если строку даты
                 разобрать не удалось.
        :rtype: datetime | None
        """
        date_raw = data.find('div', class_='date')
        date_list = date_raw.string.lower().split(' ')
        if len(date_list) > 1:
            month = months_obj[date_list[1]]
            day = int(date_list[0])
            date_object = datetime(datetime.now().year, month, day)
            return date_object

        return None

    @staticmethod
    def get_time_list(data: Tag, date: datetime) -> List[datetime]:
        """
        Извлекает список времён сеансов из блока расписания.

        Ищет внутри блока тег ``div.time_cont``, перебирает все ссылки
        ``<a>`` и преобразует их текст в объекты datetime на основе
        переданной даты. Значения, не прошедшие разбор, пропускаются.

        :param data: HTML-тег блока расписания одного дня.
        :type data: Tag
        :param date: дата, к которой привязываются времена сеансов.
        :type date: datetime
        :return: список времён сеансов, привязанных к указанной дате.
        :rtype: List[datetime]
        """
        time_list = []
        time_section_raw = data.find('div', class_='time_cont')
        time_list_raw = time_section_raw.find_all('a')
        for time_raw in time_list_raw:
            time_obj = get_time_obj(time_raw.string, date)
            if time_obj is not None:
                time_list.append(time_obj)
        return time_list

class JubiParser(ScheduleParserSite):
    """
    Парсер расписания катка «Юбилейный».

    Загружает страницу афиши :attr:`url` и формирует список расписаний
    по дням из HTML-блоков ``div.skat_item_cont``.
    """

    url = 'https://www.yubi.ru/afisha/katok/'
    """Адрес страницы афиши катка."""

    def __init__(self, utils: JubiUtils) -> None:
        """
        :param utils: класс или объект со вспомогательными методами разбора
                      расписания (по умолчанию JubiUtils).
        :type utils: JubiUtils
        """
        self.utils = utils

    def get_day_schedule_list(self) -> List[DaySchedule]:
        """
        Возвращает список расписаний по дням.

        Дни, для которых не удалось извлечь дату, в результат не включаются.

        :return: список объектов DaySchedule.
        :rtype: List[DaySchedule]
        """
        soup = self._get_soup()
        data_list = soup.find_all('div', class_='skat_item_cont')
        return [
            schedule
            for data in data_list
            if (schedule := self._build_day_schedule(data)) is not None
        ]

    def _build_day_schedule(self, data: Tag) -> DaySchedule | None:
        """
        Формирует расписание одного дня из HTML-блока расписания.

        :param data: HTML-тег блока расписания одного дня (``div.skat_item_cont``).
        :type data: Tag
        :return: объект DaySchedule либо None, если дату извлечь не удалось.
        :rtype: DaySchedule | None
        """
        date_obj = self.utils.get_date(data)
        if date_obj is None:
            return None
        time_list = self.utils.get_time_list(data, date_obj)
        return DaySchedule(date_obj, time_list)

def create_jubi_location_parser() -> LocationParser:
    """
    Создаёт LocationParser для катка «Юбилейный».

    :return: сконфигурированный LocationParser с JubiParser внутри.
    :rtype: LocationParser
    """
    return LocationParser(
        location_id=LocationId.JUBI,
        arena_name=ArenaName.JUBI,
        arena_id=ArenaId.JUBI_BASE,
        parser=JubiParser(JubiUtils()),
    )

