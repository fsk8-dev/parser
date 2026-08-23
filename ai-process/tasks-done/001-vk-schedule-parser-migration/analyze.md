# Анализ: Доработка VKScheduleParser и миграция stachek_iceberg.py

## Общее описание функциональности

Нужно привести абстрактный слой VK-парсеров к тому же стилю, что уже используется для сайтов (`ScheduleParserSite` в HEAD), и перевести парсер катка «Айсберг Арена» (screen_name сообщества `icebergkatok`) с процедурного модуля на классовую архитектуру проекта.

Сейчас расписание «Айсберга» собирается так: запрос `wall.get` → выбор актуального поста по шаблону периода и текущей дате → разбор текста регулярками → список `DaySchedule` → обёртка в `ArenaSchedule`. После изменений тот же конвейер должен идти через `VKScheduleParser` / `StachekIcebergParser` / `StachekIcebergUtils` и фабрику `create_stachek_iceberg_location_parser()`, как у `IcePalaceParser` и `JubiParser`. Точка входа `main_script.py` продолжит вызывать `handle_schedule(...)` с функцией, возвращающей `List[ArenaSchedule]`.

Задача также убирает скомпрометированный токен VK из исходников: он захардкожен в HEAD в двух местах (коммит `154c469`). Новый секрет читается из окружения (`VK_TOKEN`), `load_dotenv()` вызывается один раз в `main_script.py` до импортов парсеров. Отзыв старого токена в кабинете VK достаточен; переписывать git-историю не требуется. Файл `parse/.env.example` добавлять не нужно.

Вне скоупа: миграция `parsers/arena_tr_parser.py` (второй потребитель того же VK-конвейера).

## Связанные модули и сущности

| Модуль / файл | Назначение | Что затрагивает задача |
|---|---|---|
| `classes/schedule_parser/BaseScheduleParser.py` | ABC: свойство `url`, абстрактный `get_day_schedule_list()` | Контракт, от которого наследуется `VKScheduleParser`. В рабочем дереве слегка изменены формулировки docstring у `url`; к задаче не относится. |
| `classes/schedule_parser/ScheduleParserSite.py` (HEAD) | Абстрактный слой для HTML-сайтов: `parser_type`, `_get_response`, `_get_response_data`, `_get_soup`, переобъявленный `@abstractmethod get_day_schedule_list` | Образец стиля для доработки `VKScheduleParser` (класс, docstring'и, защищённые методы, атрибуты класса). В рабочем дереве файл переименован в `SiteScheduleParser` вместе с импортами в четырёх сайт-парсерах — это побочный WIP, не часть этой задачи. |
| `classes/schedule_parser/VKScheduleParser.py` | Абстрактный слой для VK. В HEAD — только публичный `get_post_list()` с захардкоженным токеном и `version = 5.199` (float) | Основной объект доработки: токен из env, константы класса, защищённые методы, `_get_post`, обработка ошибок, стиль. |
| `classes/LocationParser.py` | Композиция: `LocationId` / `ArenaName` / `ArenaId` / `ScheduleType` + `parser`. `get_schedule()` всегда собирает один `ArenaSchedule` из `parser.get_day_schedule_list()` | Целевая обёртка для фабрики `create_stachek_iceberg_location_parser()`. Пустой список дней даёт `ArenaSchedule` с пустым `sessionList`. `schedule_type` по умолчанию `ICE_SKATING`. |
| `classes/DaySchedule.py` | Пара `day_date` + `day_time_list` | Элемент результата `get_day_schedule_list()`. |
| `classes/ArenaSchedule.py` | Превращает список `DaySchedule` в `sessionList` из `Session` | Создаётся либо текущим `get_arena_schedule_list()`, либо `LocationParser.get_schedule()`. |
| `classes/Session.py` | Обёртка `startDate` | `format_arena_schedule()` вызывает `startDate.isoformat()`; `None` здесь падает. |
| `classes/LocationId.py`, `ArenaId.py`, `ArenaName.py`, `ScheduleType.py` | Перечисления площадок и типа расписания | Значения `STACHEK_ICEBERG` уже есть (id `9`, имя `'Айсберг Арена'`). `ScheduleType.ICE_SKATING` — текущий тип. |
| `parsers/stachek_iceberg.py` | Процедурный парсер: посты VK → актуальный пост → дни/сеансы → `List[ArenaSchedule]` | Удаляется после переноса логики в новый файл. |
| `parsers/IcePalaceParser.py`, `parsers/JubiParser.py` | Эталон классовых парсеров: `*Utils` + `*Parser(ScheduleParserSite)` + `create_*_location_parser()` | Образец структуры нового `StachekIcebergParser.py`. У `JubiUtils.get_time_list` — образец фильтрации `None` от `get_time_obj`. |
| `parsers/MagnitParser.py`, `parsers/TaurideParser.py` | Ещё два мигрированных сайт-парсера с той же схемой фабрики | Дополнительный образец фабрики; к логике VK не относятся. |
| `parsers/arena_tr_parser.py` | Второй VK-парсер на том же конвейере `get_post_list` → `get_post` | Не мигрируется. После задачи остаётся единственным потребителем `src_utils/vk_utils/get_post_list.py` и `get_post.py`. |
| `src_utils/vk_utils/get_post_list.py` | Процедурный `wall.get` по `domain` | Дублирует логику HEAD-`VKScheduleParser.get_post_list`, содержит тот же скомпрометированный токен. Останется нужен `arena_tr_parser`. |
| `src_utils/vk_utils/get_post.py` | Очистка текста поста, фильтр по `period_pattern`, проверка, что текущая дата входит в период | Логика переносится в `VKScheduleParser._get_post`; сам модуль остаётся для `arena_tr_parser`. |
| `src_utils/vk_utils/get_date_list.py` | По группам 2 и 3 шаблона периода строит список дат (год — текущий) | Используется `get_post` и напрямую `arena_tr_parser`. `_get_post` будет опираться на ту же функцию. |
| `src_utils/base_utils/get_time_obj.py` | Разбор `'HH:MM'` + дата → `datetime` либо `None` | Используется разбором сеансов «Айсберга». Сейчас `None` не отфильтровывается. |
| `src_utils/base_utils/clean_from_space.py`, `clean_from_wierd.py` | Нормализация текста поста (пробелы, «странные» символы) | Часть `clear_text` в `get_post.py`; нужны `_get_post`. |
| `src_utils/base_utils/get_time_list.py` | Разбор списка интервалов с отбрасыванием `None` | Образец фильтрации для сайт-парсеров; у «Айсберга» свой цикл по строкам. |
| `main_script.py` | Точка входа: `handle_schedule(func)` → печать, `format_arena_schedule`, POST на API | Нужны `load_dotenv()` до импортов парсеров и замена вызова `get_stachek_iceberg_schedule_list` на `stachek_iceberg_location_parser.get_schedule`. Сигнатура `handle_schedule` не меняется. |
| `requirements.txt` | Зависимости; уже есть `python-dotenv==1.0.1` и `requests==2.31.0` | Новых пакетов не требуется. |
| `.gitignore` | Содержит `.env` | `parse/.env` не в git; туда кладётся `VK_TOKEN`. |
| `ai/stachek_iceberg.1.analysis.md` | Старый разбор процедурного модуля | Контекст формата постов и regex; пути к классам устарели после переноса в `classes/`. |
| `classes/schedule_parser/.env.example` (только рабочее дерево) | Черновик плейсхолдеров, в т.ч. `VK_TOKEN=` | Против требования задачи («не добавлять `.env.example`»). К целевому результату не относится. |

## Текущие интерфейсы и API (если есть)

Ниже — контракты **закоммиченного HEAD**, от которых отталкивается описание задачи. В рабочем дереве часть из них уже частично изменена (см. последний подраздел).

### `BaseScheduleParser`

- Свойство `url: str` (не `@abstractmethod`; наследники задают атрибут класса).
- `@abstractmethod get_day_schedule_list() -> List[DaySchedule]`.

Для VK-парсеров `url` семантически — screen_name сообщества (`domain` в `wall.get`), а не URL страницы. Сейчас это нигде в VK-слое не зафиксировано.

### `ScheduleParserSite` (HEAD; образец стиля)

- Атрибут класса `parser_type`.
- Переобъявленный `@abstractmethod get_day_schedule_list()` с русским Sphinx-docstring (`:return:` / `:rtype:`).
- Защищённые `_get_response()`, `_get_response_data()`, `_get_soup()`.
- Относительные импорты внутри пакета `classes`.
- Timeout и `raise_for_status` у сайт-слоя нет — для VK это отдельное требование.

### `VKScheduleParser` (HEAD)

- Наследник `BaseScheduleParser, ABC`.
- Единственный метод: публичный `get_post_list()` без аннотаций и docstring.
- Внутри: локальные `api`, `token` (секрет в исходнике), `version = 5.199` (float).
- `requests.get` без timeout, без `raise_for_status`, без проверки ключа `'error'` в JSON. VK при ошибке API часто отвечает HTTP 200 с телом `{"error": ...}` — текущий код тогда падает на `data['response']`.
- `get_day_schedule_list` не переобъявлен (остаётся абстрактным только в базе).
- `__init__` нет, токен не инжектируется.

### `LocationParser`

- Конструктор только с keyword-only аргументами: `location_id`, `arena_name`, `arena_id`, `parser`, опционально `schedule_type=ScheduleType.ICE_SKATING`.
- `get_schedule() -> List[ArenaSchedule]`: всегда один элемент, даже если дней нет. Это и есть семантика «нет актуального поста → пустое расписание», которую нужно сохранить (сейчас её обеспечивает `get_arena_schedule_list` при `post is None`).

### Процедурный API `stachek_iceberg.py`

- `get_day_schedule_list(text, sport_schedule_pattern)` — разбор уже выбранного текста поста в `List[DaySchedule]`.
- `get_arena_schedule_list(post, skating_schedule_pattern)` — если `post is None`, дни пустые; иначе собирает `ArenaSchedule` с `LocationId/ArenaName/ArenaId.STACHEK_ICEBERG` и `ScheduleType.ICE_SKATING`.
- `get_stachek_iceberg_schedule_list()` — оркестрация: `get_post_list('icebergkatok')` → `get_post(..., period_pattern)` → `get_arena_schedule_list`. Возвращает `List[ArenaSchedule]`. Этот контракт после миграции выполняет `LocationParser.get_schedule`.

Шаблоны (нужно перенести **дословно** как атрибуты класса, без «улучшения» regex):

- период: `r'расписание.*?((\d{2}\.\d{2}).*?(\d{2}\.\d{2})).*(?=\n)'`
- массовое катание: `r'(\d{1,2}\.\d{1,2}).*\nмассовоекатание.*\n((\d{1,2}:\d{1,2}-\d{1,2}:\d{1,2}\n){0,})'`

Внутри разбора дней дополнительно используется локальный `time_pattern = r'\d{1,2}:\d{2}-\d{1,2}:\d{2}'` (в описании задачи как атрибут класса не назван).

Отладочные `print` — шесть в цикле разбора плюс ещё один `print(arena_schedule_list)` в оркестраторе; в мигрированных парсерах отладочного вывода нет (`handle_schedule` и так печатает результат).

Известный баг: после `re.search(time_pattern, time)` в список попадает результат `get_time_obj(...)` без проверки на `None`. `ArenaSchedule` кладёт его в `Session`, а `format_arena_schedule` вызывает `isoformat()` и падает. В `JubiUtils.get_time_list` и `get_time_list()` из `base_utils` `None` отбрасывается. Исправление — осознанное изменение поведения.

### VK-утилиты

- `get_post_list(domain: str)` — `wall.get` по screen_name; тот же токен и float-версия, что в HEAD-`VKScheduleParser`.
- `get_post(post_list, period_pattern) -> Optional[str]`: `clear_text` (пробелы, «странные» символы, `.lower()`), `re.match` по шаблону периода, `get_date_list`, вхождение «сегодня» в список дат. Возвращает уже очищенный текст или `None`.
- `get_date_list(text, period_pattern)` ожидает группы 2 и 3 как даты `ДД.ММ`; группа 3 может отсутствовать. Шаблон «Айсберга» даёт group 2/3 как начало и конец периода.

Импорт в `stachek_iceberg.py`: `from src_utils.vk_utils import get_post_list, get_post` при пустом `vk_utils/__init__.py` подтягивает одноимённые подмодули, а не функции (мигрированные парсеры импортируют `from ...module import func`). На целевой файл это не переносится.

### Точка входа

- `handle_schedule(get_schedule_func)` ловит любое исключение **только** вокруг вызова `get_schedule_func()`, подставляет `[]` и печатает ошибку. Падение внутри последующего `format_arena_schedule` (в том числе из-за `Session(None)`) не перехватывается и рвёт весь `init()`.
- Сейчас: `handle_schedule(get_stachek_iceberg_schedule_list)`.
- Для мигрированных площадок: `handle_schedule(xxx_location_parser.get_schedule)`.
- В HEAD `load_dotenv()` нигде нет, хотя `python-dotenv` уже в зависимостях.

### Эталон фабрики (Jubi / IcePalace)

Три сущности в одном файле PascalCase: класс утилит со `@staticmethod`, класс парсера с атрибутом `url` и `self.utils`, функция `create_*_location_parser() -> LocationParser`.

## Файлы и места в коде

| Файл | Что содержит | Что нужно изменить / создать |
|---|---|---|
| `classes/schedule_parser/VKScheduleParser.py` | HEAD: захардкоженный токен, публичный `get_post_list`. WIP уже близок к целевому виду, но не совпадает с требованиями (см. ниже) | Токен через параметр `__init__` с fallback на `os.environ['VK_TOKEN']` (fail-fast); `load_dotenv` отсюда убрать; `API_URL` / `API_VERSION='5.199'` (str); `_get_response` (timeout, params `domain=self.url`); `_get_post_list` вместо публичного метода (`raise_for_status` + ключ `'error'`); перенос логики `get_post.py` в `_get_post(period_pattern)`; переобъявить абстрактный `get_day_schedule_list`; русские Sphinx-docstring'и и type hints; относительные импорты; задокументировать screen_name в `url`. |
| `parsers/StachekIcebergParser.py` | Нет | Создать: `StachekIcebergUtils`, `StachekIcebergParser(VKScheduleParser)` с `url = 'icebergkatok'` и двумя шаблонами-атрибутами класса, фабрика `create_stachek_iceberg_location_parser()`. Без `print`. `get_day_schedule_list()` при отсутствии поста возвращает `[]`. `None` от `get_time_obj` отфильтровывать. |
| `parsers/stachek_iceberg.py` | Процедурная реализация | Удалить после переноса. |
| `main_script.py` | Оркестрация всех площадок | `load_dotenv()` один раз в самом верху, до импортов парсеров; подключить фабрику «Айсберга» и вызвать `handle_schedule(stachek_iceberg_location_parser.get_schedule)` вместо `get_stachek_iceberg_schedule_list`. `handle_schedule` / `format_arena_schedule` / `send_schedule` не менять. |
| `src_utils/vk_utils/get_post.py` | Выбор актуального поста | Логика копируется в `VKScheduleParser._get_post`. Файл **не удалять**: нужен `arena_tr_parser`. |
| `src_utils/vk_utils/get_post_list.py` | Процедурный `wall.get` с тем же секретом | Не удалять. После отзыва токена вызовы `arena_tr` с захардкоженным значением перестанут работать. Задача не мигрирует `arena_tr`, но секрет из этого файла всё равно нужно убрать из репозитория. |
| `src_utils/vk_utils/get_date_list.py` | Раскрытие периода в список дат | Остаётся общей зависимостью `_get_post` и `arena_tr_parser`. |
| `classes/LocationId.py`, `ArenaId.py`, `ArenaName.py` | Значения `STACHEK_ICEBERG` уже заданы | Не менять. |
| `classes/LocationParser.py` | Композиция и `get_schedule` | Не менять; фабрика только собирает экземпляр. |
| `parse/.env` | Локальные секреты, в git не входит; `VK_TOKEN` уже заведена | Новый токен кладётся сюда вручную; в репозиторий не попадает. `.env.example` не создавать. |
| Тесты | Каталога `test/` нет | Автотестов нет; проверка — ручной прогон против живого VK API и просмотр `print(arena_schedule_list)` в `handle_schedule`. |
| `docs/` | Нет | Документации проекта нет. |

## Зависимости и ограничения

- **Внешние:** `requests` (VK API), `python-dotenv` (уже в `requirements.txt`). Живой `wall.get`, версия API 5.199, параметр `domain` = screen_name. Формат постов сообщества `icebergkatok` должен по-прежнему начинаться с «расписание» и содержать блок «массовое катание» — шаблоны после очистки текста (без пробелов, lower).
- **Токен:** значение из коммита `154c469` скомпрометировано. Достаточно отозвать его в кабинете приложения VK и положить новый в `parse/.env`. Историю git не переписывать. В анализе и в коде секрет не повторять.
- **`load_dotenv`:** фабрики мигрированных парсеров вызываются на уровне модуля в `main_script.py`, значит `__init__` `VKScheduleParser` отработает в момент импорта. `load_dotenv()` обязан идти раньше этих импортов. Повторный вызов внутри `VKScheduleParser` не нужен и расходится с требованием «один раз в точке входа».
- **Fail-fast vs тесты:** чтение `os.environ['VK_TOKEN']` при отсутствии переменной даёт `KeyError`. Параметр `token` в `__init__` позволяет обойти env в тестах. Тестов в репозитории сейчас нет.
- **`arena_tr_parser` остаётся на старом конвейере.** `get_post_list.py` / `get_post.py` удалять нельзя. Пока в `get_post_list` лежит отозванный (или опустошённый) токен, площадка TR будет получать пустое расписание через `handle_schedule`. Это ограничение соседнего модуля, не миграция TR.
- **Семантика пустого поста:** `get_day_schedule_list() -> []`, но `LocationParser.get_schedule()` всё равно вернёт список из одного `ArenaSchedule` с пустым `sessionList` — как текущий `get_arena_schedule_list`.
- **Исправление `None`:** меняет поведение относительно текущего кода; в MR/коммите это нужно явно отметить.
- **Regex:** копировать дословно. `get_post` использует `re.match` (якорь на начало строки) после `clear_text`; `get_date_list` — `re.search` по тому же шаблону. Менять это при переносе нельзя, иначе выбор поста разъедется с `arena_tr`.
- **Верификация:** тестов нет. Ошибка внутри `get_schedule` выглядит как пустой список и печать исключения; ошибка в `format_arena_schedule` валит весь прогон. Первый запуск после миграции смотреть по выводу `arena_schedule_list`.
- **Побочный WIP в рабочем дереве (не цель задачи, но влияет на текущие файлы):**
  - `ScheduleParserSite` переименован в `SiteScheduleParser` (файл + 4 парсера). Описание задачи опирается на имя HEAD `ScheduleParserSite`.
  - `VKScheduleParser` уже частично переписан: есть `API_URL`/`API_VERSION` (str), `_get_response` с `timeout=10`, `_get_post_list` с `raise_for_status` и проверкой `'error'`, абстрактный `get_day_schedule_list`, относительные импорты. Нет `_get_post`. `load_dotenv()` всё ещё внутри модуля. Проверка `if token is None` смотрит на аргумент, а не на итоговое `self.token`: при `token=None` и заданном `VK_TOKEN` в env конструктор всё равно бросает `RuntimeError`. Используется `os.getenv`, а не `os.environ['VK_TOKEN']`.
  - В `get_post_list.py` токен заменён на пустую строку (секрет из файла убран, вызовы TR без env сломаны).
  - В `main_script.py` уже добавлен `load_dotenv()` сверху, но вызов всё ещё `get_stachek_iceberg_schedule_list`.
  - Появился `classes/schedule_parser/.env.example` — по дополнительному требованию задачи его добавлять не следует.
)
