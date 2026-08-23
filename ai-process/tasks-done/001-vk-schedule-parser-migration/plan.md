# План реализации: Доработка VKScheduleParser и миграция stachek_iceberg.py

Привести `VKScheduleParser` к стилю `SiteScheduleParser` (токен из env, константы класса, защищённые методы, обработка ошибок, docstring'и) и перевести парсер катка «Айсберг Арена» с процедурного модуля `parsers/stachek_iceberg.py` на классовую архитектуру (`StachekIcebergUtils` + `StachekIcebergParser` + фабрика). Точка входа переключается на `LocationParser.get_schedule`, старый модуль удаляется. Рабочее дерево уже содержит часть доработок `VKScheduleParser` — план учитывает их как основу и описывает целевое состояние.

## 1. Доработать `VKScheduleParser`

**Файл (изменить):** `classes/schedule_parser/VKScheduleParser.py`

Относительно текущего WIP нужно:

1. **Убрать `load_dotenv()` из модуля** — удалить строки `from dotenv import load_dotenv` и `load_dotenv()` в начале файла. Загрузка `.env` происходит один раз в `main_script.py` (уже сделано в WIP), т.к. фабрики вызываются на уровне модуля и `__init__` отработает в момент импорта.
2. **Исправить логику токена в `__init__`** — сейчас проверка `if token is None` смотрит на аргумент, а не на итоговое значение, и используется `os.getenv`. Целевое поведение: параметр `token` с fallback на `os.environ['VK_TOKEN']` (fail-fast через `KeyError`, если переменной нет); явный параметр позволяет обойти env в тестах.
3. **Добавить `_get_post(period_pattern)`** — дословный перенос логики `src_utils/vk_utils/get_post.py`: очистка текста (`clean_from_space` → `clean_from_wierd` → `lower`), фильтр через `re.match` (якорь на начало строки — важно, не `re.search`), проверка вхождения текущей даты в `get_date_list`. Возвращает очищенный текст поста или `None`.
4. **Задокументировать**, что для VK-парсеров `url` хранит screen_name сообщества (параметр `domain` метода `wall.get`), а не URL страницы.
5. Остальное в WIP уже соответствует цели и сохраняется: `API_URL` / `API_VERSION = '5.199'` (str) как атрибуты класса, `_get_response` с `timeout=10` и `domain=self.url`, `_get_post_list` с `raise_for_status()` и проверкой ключа `'error'`, переобъявленный `@abstractmethod get_day_schedule_list`, относительные импорты внутри пакета `classes`.

Целевой вид файла:

```python
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

import requests

from .BaseScheduleParser import BaseScheduleParser
from ..DaySchedule import DaySchedule
from src_utils.base_utils.clean_from_space import clean_from_space
from src_utils.base_utils.clean_from_wierd import clean_from_wierd
from src_utils.vk_utils.get_date_list import get_date_list


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

    def _get_post(self, period_pattern: str) -> str | None:
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

        post_list = self._get_post_list()
        post_list_text = list(map(lambda post: self._clear_text(post['text']), post_list))
        post_list_filtered = list(filter(lambda text: re.match(period_pattern, text), post_list_text))

        for post_text in post_list_filtered:
            if date_now in get_date_list(post_text, period_pattern):
                return post_text

        return None

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
        return clean_from_wierd(clean_from_space(text)).lower()
```

Обратить внимание:
- Порядок очистки (`clean_from_space` → `clean_from_wierd` → `lower`) и `re.match` вместо `re.search` — дословно как в `get_post.py`, иначе выбор поста разъедется с `arena_tr_parser`, который остаётся на старом конвейере.
- `get_date_list` остаётся общей зависимостью в `src_utils/vk_utils/get_date_list.py` — не переносить и не дублировать.

## 2. Создать `StachekIcebergParser`

**Файл (создать):** `parsers/StachekIcebergParser.py`

Три сущности в одном файле по образцу `parsers/JubiParser.py`: класс утилит со `@staticmethod`, класс парсера, фабрика. Шаблоны `PERIOD_PATTERN` и `SKATING_SCHEDULE_PATTERN` — атрибуты класса парсера, **скопировать дословно** из `stachek_iceberg.py` без «улучшений» regex. Отладочные `print` (6 мест в разборе + 1 в оркестраторе) не переносятся. `None` от `get_time_obj` отфильтровывается (исправление бага, как в `JubiUtils.get_time_list`) — осознанное изменение поведения, отметить в коммите/MR.

```python
import
    re
from datetime import
    datetime
from typing import
    List

from classes.ArenaId import
    ArenaId
from classes.ArenaName import
    ArenaName
from classes.DaySchedule import
    DaySchedule
from classes.LocationId import
    LocationId
from classes.LocationParser import
    LocationParser
from classes.schedule_parser.VKScheduleParser import
    VKScheduleParser
from src_utils.base_utils.get_time_obj import
    get_time_obj


class StachekIcebergUtils:
    """
    Вспомогательные методы разбора текста поста расписания катка
    «Айсберг Арена».

    Расписание в очищенном тексте поста представлено блоками вида
    ``«<дата>\\nмассовоекатание\\n<интервалы HH:MM-HH:MM>»``.
    """

    TIME_PATTERN = r'\d{1,2}:\d{2}-\d{1,2}:\d{2}'
    """Шаблон строки интервала времени сеанса."""

    @staticmethod
    def get_date(
            match: tuple) -> datetime:
        """
        Извлекает дату дня из совпадения шаблона расписания.

        Группа 1 совпадения содержит день и месяц вида ``«17.08»``;
        год берётся текущий.

        :param match: кортеж групп совпадения SKATING_SCHEDULE_PATTERN.
        :type match: tuple
        :return: дата дня расписания.
        :rtype: datetime
        """
        return datetime.strptime(
            f'{match[0]}.{datetime.now().year}',
            '%d.%m.%Y')

    @staticmethod
    def get_time_list(
            time_list_raw:
            List[
                str],
            date: datetime) ->
    List[
        datetime]:
        """
        Извлекает список времён сеансов из строк интервалов.

        Строки, не соответствующие шаблону :attr:`TIME_PATTERN`,
        пропускаются. Значения, которые ``get_time_obj`` не смог
        разобрать (None), в результат не включаются.

        :param time_list_raw: строки блока времён сеансов.
        :type time_list_raw: List[str]
        :param date: дата, к которой привязываются времена сеансов.
        :type date: datetime
        :return: список времён начала сеансов.
        :rtype: List[datetime]
        """
        time_list = []
        for time in time_list_raw:
            if re.search(
                    StachekIcebergUtils.TIME_PATTERN,
                    time):
                time_obj = get_time_obj(
                    time.split(
                        '-')[
                        0],
                    date)
                if time_obj is not None:
                    time_list.append(
                        time_obj)
        return time_list


class StachekIcebergParser(
    VKScheduleParser):
    """
    Парсер расписания катка «Айсберг Арена».

    Выбирает актуальный пост сообщества :attr:`url` по шаблону
    :attr:`PERIOD_PATTERN` и формирует список расписаний по дням
    из блоков массового катания.
    """

    url = 'icebergkatok'
    """screen_name сообщества ВКонтакте катка."""

    PERIOD_PATTERN = r'расписание.*?((\d{2}\.\d{2}).*?(\d{2}\.\d{2})).*(?=\n)'
    """Шаблон строки периода расписания в очищенном тексте поста."""

    SKATING_SCHEDULE_PATTERN = r'(\d{1,2}\.\d{1,2}).*\nмассовоекатание.*\n((\d{1,2}:\d{1,2}-\d{1,2}:\d{1,2}\n){0,})'
    """Шаблон блока массового катания в очищенном тексте поста."""

    def __init__(
            self,
            utils: StachekIcebergUtils,
            token: str | None = None) -> None:
        """
        :param utils: класс или объект со вспомогательными методами разбора
                      текста поста (по умолчанию StachekIcebergUtils).
        :type utils: StachekIcebergUtils
        :param token: токен доступа VK API (см. VKScheduleParser).
        :type token: str | None
        """
        super().__init__(
            token=token)
        self.utils = utils

    def get_day_schedule_list(
            self) ->
    List[
        DaySchedule]:
        """
        Возвращает список расписаний по дням из актуального поста.

        Если актуальный пост не найден, возвращается пустой список —
        LocationParser при этом всё равно создаст ArenaSchedule
        с пустым sessionList.

        :return: список объектов DaySchedule.
        :rtype: List[DaySchedule]
        """
        post = self._get_posts_with_schedule(
            self.PERIOD_PATTERN)
        if post is None:
            return []
        day_schedule_list = []
        for match in re.findall(
                self.SKATING_SCHEDULE_PATTERN,
                post):
            date = self.utils.get_date(
                match)
            time_list = self.utils.get_time_list(
                match[
                    1].split(
                    '\n'),
                date)
            day_schedule_list.append(
                DaySchedule(
                    date,
                    time_list))
        return day_schedule_list


def create_stachek_iceberg_location_parser() -> LocationParser:
    """
    Создаёт LocationParser для катка «Айсберг Арена».

    :return: сконфигурированный LocationParser с StachekIcebergParser внутри.
    :rtype: LocationParser
    """
    return LocationParser(
        location_id=LocationId.STACHEK_ICEBERG,
        arena_name=ArenaName.STACHEK_ICEBERG,
        arena_id=ArenaId.STACHEK_ICEBERG,
        parser=StachekIcebergParser(
            StachekIcebergUtils()),
    )
```

## 3. Обновить точку входа

**Файл (изменить):** `main_script.py`

- `load_dotenv()` в самом верху (строки 1–2) уже есть в WIP — оставить как есть, он обязан идти раньше импортов парсеров, т.к. фабрика отработает в момент импорта.
- Заменить импорт процедурного модуля на фабрику (рядом с остальными мигрированными площадками):

```python
from parsers.StachekIcebergParser import create_stachek_iceberg_location_parser
stachek_iceberg_location_parser = create_stachek_iceberg_location_parser()
```

- Удалить строку `from parsers.stachek_iceberg import get_stachek_iceberg_schedule_list`.
- В `init()` заменить вызов:

```python
handle_schedule(stachek_iceberg_location_parser.get_schedule)
```

вместо `handle_schedule(get_stachek_iceberg_schedule_list)`. `handle_schedule`, `format_arena_schedule`, `send_schedule` не менять — контракт `List[ArenaSchedule]` сохраняется.

## 4. Удалить старый процедурный модуль

**Файл (удалить):** `parsers/stachek_iceberg.py`

Перед удалением убедиться, что единственный импорт (`main_script.py`, строка 10) уже заменён в шаге 3. `src_utils/vk_utils/get_post_list.py`, `get_post.py`, `get_date_list.py` **не удалять** — они нужны оставшемуся на старом конвейере `parsers/arena_tr_parser.py`.

## 5. Убрать черновик `.env.example`

**Файл (удалить):** `classes/schedule_parser/.env.example`

Файл есть только в рабочем дереве (уже в индексе) и противоречит требованию задачи «не добавлять `.env.example` с пустыми плейсхолдерами». Убрать из индекса и удалить:

```bash
git rm --cached classes/schedule_parser/.env.example && rm classes/schedule_parser/.env.example
```

## 6. Операции с токеном VK (вручную, вне кода)

- Отозвать скомпрометированный токен в кабинете приложения VK (достаточно отзыва, git-историю не переписывать).
- Перевыпустить токен и положить новый в `parse/.env` (переменная `VK_TOKEN` там уже заведена; файл в `.gitignore`, в репозиторий не попадёт).
- После отзыва токена `parsers/arena_tr_parser.py` (пустой токен в `get_post_list.py`) начнёт получать пустое расписание через `handle_schedule` — известное ограничение, миграция TR вне скоупа задачи.

## 7. Тесты

**Файл (создать, опционально):** `tests/test_stachek_iceberg_parser.py`

В проекте тестов нет и по `description.md` верификация — ручная против живого VK API, поэтому автотесты опциональны. Если добавлять — только на stdlib (`unittest` + `unittest.mock`), новых зависимостей в `requirements.txt` не требуется. Параметр `token` в `__init__` позволяет обойти env.

Сценарии:
- Happy path: `get_day_schedule_list` с замоканным `_get_post`, возвращающим образец очищенного текста поста → список `DaySchedule` с корректными датами (год — текущий) и временами начала сеансов.
- Нет актуального поста: `_get_post` возвращает `None` → `get_day_schedule_list()` возвращает `[]`, а `LocationParser.get_schedule()` всё равно отдаёт список из одного `ArenaSchedule` с пустым `sessionList`.
- Фильтрация `None`: строка интервала, которую `get_time_obj` не разбирает → значение не попадает в `day_time_list` (регрессия на исправленный баг с `Session(None)`).
- Ошибка VK API: замоканный `requests.get` с телом `{"error": {...}}` → `_get_post_list` бросает `ValueError`.
- Fail-fast токена: `VKScheduleParser()` без параметра и без `VK_TOKEN` в окружении → `KeyError`; с явным `token='...'` → конструктор отрабатывает без env.

Обязательная ручная верификация (основная по задаче): прогон `python main_script.py` с действующим `VK_TOKEN` в `parse/.env`; в выводе `print('arena_schedule_list: ', ...)` проверить, что у `STACHEK_ICEBERG` непустой `sessionList` с ожидаемыми датами/временами. Ошибка миграции проявится как пустое расписание (исключение перехватывается в `handle_schedule`), а не как падение прогона.

## Сводка файлов

| Действие | Файл |
|----------|------|
| Изменить | `classes/schedule_parser/VKScheduleParser.py` |
| Создать  | `parsers/StachekIcebergParser.py` |
| Изменить | `main_script.py` |
| Удалить  | `parsers/stachek_iceberg.py` |
| Удалить  | `classes/schedule_parser/.env.example` |
| Создать (опционально) | `tests/test_stachek_iceberg_parser.py` |

Не трогаем: `src_utils/vk_utils/get_post_list.py`, `src_utils/vk_utils/get_post.py`, `src_utils/vk_utils/get_date_list.py` (нужны `arena_tr_parser`), `classes/LocationParser.py`, `classes/LocationId.py` / `ArenaId.py` / `ArenaName.py` / `ScheduleType.py` (значения `STACHEK_ICEBERG` уже есть), `requirements.txt` (новых зависимостей нет), `parsers/arena_tr_parser.py` (вне скоупа).

## Ссылки
- [analyze.md текущей задачи](analyze.md)
- [description.md текущей задачи](description.md)
- Образец стиля: `classes/schedule_parser/SiteScheduleParser.py`, `parsers/JubiParser.py`
- Старый разбор формата постов: `ai/stachek_iceberg.1.analysis.md`
