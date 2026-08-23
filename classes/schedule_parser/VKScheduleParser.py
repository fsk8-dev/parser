import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List

import requests

from src_utils.DateTimeCustomUtils import DateTimeCustomUtils
from src_utils.TextUtils import TextUtils
from .BaseScheduleParser import BaseScheduleParser
from ..DaySchedule import DaySchedule


class VKScheduleParser(BaseScheduleParser, ABC):
    """
    Абстрактный базовый класс парсера расписания, получающего данные
    из постов сообщества ВКонтакте.

    Инкапсулирует запрос к методу ``wall.get`` VK API и выбор актуального
    поста расписания. Для VK-парсеров :attr:`url` хранит screen_name
    сообщества (параметр ``domain`` метода ``wall.get``), а не URL страницы.
    Наследникам достаточно переопределить :attr:`url` и реализовать
    :meth:`get_day_schedule_list`.
    """

    API_URL = 'https://api.vk.com/method/wall.get'
    """URL метода wall.get VK API."""

    API_VERSION = '5.199'
    """Версия VK API."""

    def __init__(self, token: str | None = None) -> None:
        """
        :param token: токен доступа VK API. Если не передан, читается
                      из переменной окружения ``VK_TOKEN``.
        :type token: str | None
        :raises KeyError: если токен не передан и ``VK_TOKEN`` не задан.
        """
        if token is None:
            token = os.environ['VK_TOKEN']
        self.token = token

    @abstractmethod
    def get_day_schedule_list(self) -> List[DaySchedule]:
        """
        Возвращает список расписаний по дням, извлечённый из постов сообщества.

        :return: список объектов DaySchedule.
        :rtype: List[DaySchedule]
        """
        ...

    def _get_response(self) -> requests.Response:
        """
        Выполняет запрос к wall.get для сообщества :attr:`url`.

        :return: ответ сервера VK API.
        :rtype: requests.Response
        """
        return requests.get(
            self.API_URL,
            params={
                'access_token': self.token,
                'v': self.API_VERSION,
                'domain': self.url,
            },
            timeout=10,
        )

    def _get_post_list(self) -> List[dict]:
        """
        Возвращает список постов сообщества из ответа VK API.

        :raises ValueError: если VK API вернул ошибку в теле ответа
                            (VK отвечает HTTP 200 с телом {"error": ...}).
        :return: список постов (items) из ответа wall.get.
        :rtype: List[dict]
        """
        response = self._get_response()
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            raise ValueError(f"VK API error: {data['error'].get('error_msg')}")
        return data['response']['items']

    def _get_posts_with_schedule(self, period_pattern: str) -> List[str]:
        """
        Возвращает очищенный текст актуального поста расписания.

        Пост считается актуальным, если его очищенный текст начинается
        с шаблона периода и текущая дата входит в этот период.

        :param period_pattern: шаблон периода расписания; группы 2 и 3
                               должны давать даты начала и конца периода.
        :type period_pattern: str
        :return: очищенный текст поста либо None, если актуальный пост
                 не найден.
        :rtype: str | None
        """
        date_format = '%d.%m.%Y'
        date_now = datetime.strptime(datetime.now().strftime(date_format), date_format)
        date_next_week = date_now + timedelta(days=7)

        post_list = self._get_post_list()
        post_list_text = list(map(lambda post: self._clear_text(post['text']), post_list))
        post_list_filtered = list(filter(lambda text: re.match(period_pattern, text), post_list_text))

        result = []
        for post_text in post_list_filtered:
            date_period = DateTimeCustomUtils.get_date_list(post_text, period_pattern)
            if date_now in date_period or date_next_week in date_period:
                result.append(post_text)
        return result

    @staticmethod
    def _clear_text(text: str) -> str:
        """
        Нормализует текст поста: убирает пробелы и «странные» символы,
        приводит к нижнему регистру.

        :param text: исходный текст поста.
        :type text: str
        :return: очищенный текст.
        :rtype: str
        """
        cleaned = TextUtils.clean_from_wierd(text)
        cleaned = TextUtils.clean_from_space(cleaned)
        return cleaned.lower()
