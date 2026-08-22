import re
from datetime import datetime
from typing import List

from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.DaySchedule import DaySchedule
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser
from classes.schedule_parser.ScheduleParserSite import ScheduleParserSite
from src_utils.base_utils.clean_from_space import clean_from_space
from src_utils.base_utils.get_time_list import get_time_list
from src_utils.base_utils.months_obj import months_obj

class IcePalaceUtils:
    """
    Вспомогательные методы для разбора расписания «Ледового дворца».

    Расписание на странице представлено сплошным текстом: дата вида
    ``"21августа"`` (или период ``"21-23августа"``), двоеточие и список
    интервалов сеансов через ``;`` — ``"21августа:10:00-11:00;12:00-13:00;"``.
    """

    @staticmethod
    def get_data_list(soup) -> List[str]:
        data_list = []
        text = clean_from_space(soup.text)
        pattern = r'((\d{1,2}-)?\d{1,2}[а-яА-Я]{3,9}:(\d{1,2}\s*:\s*\d{2}-\d{1,2}\s*:\s*\d{2}\s*;?)*)'
        matches = re.findall(pattern, text)
        for match in matches:
            item = match[0]
            data_list.append(item)
        return data_list

    @staticmethod
    def is_date_period(date_string: str) -> bool:
        """
        Проверяет, является ли строка даты периодом вида ``"21-23 августа"``.

        :param date_string: нормализованная строка даты (день и месяц разделены пробелом).
        :type date_string: str
        :return: True, если строка описывает период дат.
        :rtype: bool
        """
        pattern = r'\d{1,2}\s*-\s*\d{1,2}\s*[а-я]{1,8}'
        return re.search(pattern, date_string) is not None

    @staticmethod
    def get_day(date_string: str) -> datetime | None:
        """
        Разбирает строку одиночной даты вида ``"21 августа"``.

        Год берётся текущий, название месяца переводится в номер через
        ``months_obj``.

        :param date_string: строка даты, например ``"21 августа"``.
        :type date_string: str
        :return: дата дня расписания либо None, если строку разобрать не удалось.
        :rtype: datetime | None
        """
        temp_list = date_string.split(' ')
        if len(temp_list) == 2:
            return datetime(datetime.now().year, months_obj[temp_list[1]], int(temp_list[0]))
        return None

    @staticmethod
    def get_day_list_from_date_period(date_string: str) -> List[datetime]:
        """
        Раскрывает период вида ``"21-23 августа"`` в список дат.

        :param date_string: строка периода, например ``"21-23 августа"``.
        :type date_string: str
        :return: список дат периода включительно; пустой список, если
                 строку разобрать не удалось.
        :rtype: List[datetime]
        """
        day_list = []
        temp_list = [item for item in date_string.replace('-', ' ').split(' ') if item != '']
        if len(temp_list) == 3:
            month = months_obj[temp_list[2]]
            for day in range(int(temp_list[0]), int(temp_list[1]) + 1):
                day_list.append(datetime(datetime.now().year, month, day))
        return day_list

    @staticmethod
    def normalize_date_string(date_string: str) -> str | None:
        """
        Нормализует строку даты: отделяет пробелом число от названия месяца.

        ``"21августа"`` → ``"21 августа"``,
        ``"21-23августа"`` → ``"21-23 августа"``.

        :param date_string: сырая строка даты без пробелов.
        :type date_string: str
        :return: нормализованная строка либо None, если название месяца
                 не найдено.
        :rtype: str | None
        """
        matches = re.findall(r'(.*?)([а-яА-Я]+)', date_string)
        if not matches:
            return None
        return ' '.join([matches[0][0], matches[0][1]])

class IcePalaceParser(ScheduleParserSite):
    """
    Парсер расписания «Ледового дворца».
    Загружает страницу :attr:`url` и формирует список расписаний по дням
    из текстовых строк вида ``"21августа:10:00-11:00;"``.
    """
    url = 'https://newarena.spb.ru/rink/'

    def __init__(self, utils:  IcePalaceUtils) -> None:
        """
        :param utils: класс или объект со вспомогательными методами разбора
                      расписания
        :type utils: IcePalaceUtils
        """
        self.utils = utils

    def get_day_schedule_list(self) -> List[DaySchedule]:
        soup = self._get_soup()
        data_list = self.utils.get_data_list(soup)

        result = []
        for data in data_list:
            result.extend(self._build_day_schedule(data))
        return result

    def _build_day_schedule(self, data: str) -> List[DaySchedule]:
        """
        Формирует расписание из одной строки расписания.
        Строка вида ``"21августа:10:00-11:00;"`` даёт один день, строка
        с периодом ``"21-23августа:10:00-11:00;"`` — по объекту DaySchedule
        на каждую дату периода.
        :param data: строка расписания из ``IcePalaceUtils.get_data_list``.
        :type data: str
        :return: список объектов DaySchedule (пустой, если дату разобрать
                 не удалось).
        :rtype: List[DaySchedule]
        """
        temp_list = data.split(':', 1)
        if len(temp_list) != 2:
            return []
        date_string = self.utils.normalize_date_string(temp_list[0].strip())
        if date_string is None:
            return []
        if self.utils.is_date_period(date_string):
            day_list = self.utils.get_day_list_from_date_period(date_string)
        else:
            day = self.utils.get_day(date_string)
            day_list = [day] if day is not None else []
        return [
            DaySchedule(day, get_time_list(temp_list[1].strip(), day))
            for day in day_list
        ]

def create_ice_palace_location_parser() -> LocationParser:
    """
    Создаёт LocationParser для «Ледового дворца».

    :return: сконфигурированный LocationParser с IcePalaceParser внутри.
    :rtype: LocationParser
    """
    return LocationParser(
        location_id=LocationId.ICE_PALACE,
        arena_name=ArenaName.ICE_PALACE,
        arena_id=ArenaId.ICE_PALACE,
        parser=IcePalaceParser(IcePalaceUtils()),
    )
