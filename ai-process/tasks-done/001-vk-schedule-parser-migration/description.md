# Задача: Доработка VKScheduleParser и миграция stachek_iceberg.py на него

## Суть задачи
Привести абстрактный класс `VKScheduleParser` к стилю проекта (по образцу `ScheduleParserSite`): убрать захардкоженный токен VK в `.env`, добавить защищённые методы, docstring'и, типизацию и обработку ошибок. Затем мигрировать парсер `parsers/stachek_iceberg.py` со старого процедурного стиля на классовую архитектуру: `StachekIcebergParser(VKScheduleParser)` + `StachekIcebergUtils` + фабрика `create_stachek_iceberg_location_parser()`, по образцу `IcePalaceParser` / `JubiParser`.

## Детали и требования

### Доработка `VKScheduleParser` (`classes/schedule_parser/VKScheduleParser.py`)
- **Токен**: отозвать текущий (скомпрометирован — лежит в открытом виде в git-истории, коммит `154c469`), перевыпустить в кабинете приложения VK, положить новый в `parse/.env` (переменная `VK_TOKEN` там уже заведена). В коде читать через `os.environ['VK_TOKEN']` (fail-fast), `load_dotenv()` вызвать один раз в точке входа `main_script.py` до импортов парсеров. Токен передавать в `__init__` (параметр с fallback на env — удобно для тестов).
- **Константы**: `API_URL` и `API_VERSION` — атрибуты класса (как `parser_type` у `ScheduleParserSite`); версию хранить строкой `'5.199'`, а не float.
- **Методы**: защищённые `_get_response()` и `_get_post_list()` (вместо публичного `get_post_list`); добавить `_get_post(period_pattern)` — перенос логики `src_utils/vk_utils/get_post.py` (очистка текста, фильтр по шаблону периода, проверка вхождения текущей даты), т.к. последовательность «посты → актуальный пост» общая для обоих VK-парсеров.
- **Контракт**: переобъявить `get_day_schedule_list()` как `@abstractmethod` с docstring (как в `ScheduleParserSite`).
- **Обработка ошибок**: `response.raise_for_status()`, `timeout` у `requests.get`, явная проверка `'error'` в теле ответа VK (VK возвращает 200 с телом ошибки).
- **Стиль**: русские Sphinx-style docstring'и (`:param:` / `:type:` / `:return:` / `:rtype:`), type hints, относительные импорты внутри пакета `classes` (`from .BaseScheduleParser import ...`).
- Задокументировать, что для VK-парсеров `url` хранит screen_name сообщества, а не URL страницы.

### Миграция `stachek_iceberg.py`
- Новый файл `parsers/StachekIcebergParser.py` (именование PascalCase по имени класса) с тремя сущностями: `StachekIcebergUtils` (статические хелперы разбора текста поста), `StachekIcebergParser(VKScheduleParser)`, фабрика `create_stachek_iceberg_location_parser() -> LocationParser`.
- `url = 'icebergkatok'`; шаблоны `PERIOD_PATTERN` и `SKATING_SCHEDULE_PATTERN` — атрибуты класса, **скопировать дословно** без «улучшений» regex.
- Удалить всю `print`-отладку (6 мест) — в новом стиле парсеров отладочного вывода нет.
- Сохранить семантику «нет актуального поста → пустое расписание»: `get_day_schedule_list()` возвращает `[]`, `LocationParser.get_schedule()` всё равно создаёт `ArenaSchedule` с пустым `sessionList`.
- Исправить существующий баг: `get_time_obj` может вернуть `None`, а текущий код добавляет его в `time_list` без проверки (дальше `Session(None)` падает на `isoformat()` в `format_arena_schedule`). В новой реализации `None` отфильтровывать (как в `JubiUtils.get_time_list`). Это осознанное изменение поведения — отметить в MR/коммите.
- `main_script.py`: заменить импорт и вызов `handle_schedule(get_stachek_iceberg_schedule_list)` на `handle_schedule(stachek_iceberg_location_parser.get_schedule)`; `handle_schedule()` не меняется (контракт `List[ArenaSchedule]` сохраняется).
- Удалить старый `parsers/stachek_iceberg.py`.

## Контекст
- Целевая архитектура проекта: `BaseScheduleParser` (ABC) → абстрактные прослойки по типу источника (`ScheduleParserSite` для сайтов, `VKScheduleParser` для ВК) → конкретные парсеры в `parsers/` с фабриками `create_xxx_location_parser()`, возвращающими `LocationParser` (композиция: `LocationId`/`ArenaName`/`ArenaId`/`ScheduleType` + parser).
- Значения `STACHEK_ICEBERG` уже есть в `LocationId` (=9), `ArenaId` (=9), `ArenaName` (='Айсберг Арена').
- `parse/.env` существует и корректно проигнорирован git (`.gitignore` содержит `.env`, файл не отслеживается); `python-dotenv==1.0.1` уже в `requirements.txt`, но `load_dotenv()` нигде не вызывается.
- Токен продублирован в двух файлах: `classes/schedule_parser/VKScheduleParser.py:9` и `src_utils/vk_utils/get_post_list.py:6` — после миграции дублирование устраняется заодно.
- `parsers/arena_tr_parser.py` использует тот же VK-конвейер (`get_post_list` → `get_post` → разбор текста) — кандидат на аналогичную миграцию; после неё `src_utils/vk_utils/get_post_list.py` и `get_post.py` станут ненужными.
- Тестов в проекте нет — верификация только ручная против живого API VK; `handle_schedule()` в `main_script.py` перехватывает исключения, поэтому ошибка миграции проявится как пустое расписание, а не падение — при первом запуске смотреть вывод `print(arena_schedule_list)`.
- Существующий анализ модуля: `parse/ai/stachek_iceberg.1.analysis.md`.

## дополнительно 
- не Мигрировать  `arena_tr_parser.py` в рамках этой же задачи
- Достаточно отзыва токена в VK
- не Добавлять `parse/.env.example` с пустыми плейсхолдерами переменных 
