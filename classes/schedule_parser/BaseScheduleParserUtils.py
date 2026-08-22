from datetime import datetime
from typing import List

from bs4 import Tag

from src_utils.base_utils.get_time_obj import get_time_obj


class BaseScheduleParserUtils:
    """
    Базовый набор вспомогательных методов для парсеров расписания.

    Содержит статические методы извлечения данных из HTML-разметки,
    общие для парсеров, работающих с типовой структурой страницы
    (блок ``div.time_cont`` со ссылками-временами).
    """

    @staticmethod
    def get_time_list(data: Tag, date: datetime) -> List[datetime]:
        """
        Извлекает список времён сеансов из HTML-блока расписания.

        Ищет внутри переданного тега блок ``div.time_cont``, перебирает все
        ссылки ``<a>`` в нём и преобразует их текст в объекты datetime
        на основе переданной даты. Значения, не прошедшие разбор
        (``get_time_obj`` вернул None), пропускаются.

        :param data: HTML-тег, содержащий блок расписания с временами сеансов.
        :type data: Tag
        :param date: дата, к которой привязываются извлекаемые времена.
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
