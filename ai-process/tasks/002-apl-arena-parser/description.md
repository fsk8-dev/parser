# Задача: Парсер расписания APL Арена (ВКонтакте)

## Суть задачи
Создать `parsers/APLArenaParser.py` по аналогии с `parsers/StachekIcebergParser.py`:
utils-класс + парсер `APLArenaParser(VKScheduleParser)` + фабрика
`create_apl_arena_location_parser()`. Парсер выбирает актуальный пост сообщества
`club238896923` и формирует список `DaySchedule` из блоков с датами.
Также добавить значения `APL_ARENA` в enum'ы и зарегистрировать парсер в `main_script.py`.

## Детали и требования
- `url = 'club238896923'` (screen_name сообщества ВКонтакте).
- Строка идентификации и периода: «Расписание массовых катаний с 15 по 21 августа».
- Текст даты дня: «Суббота 15 августа».
- Очищенный текст поста не содержит пробелов и в нижнем регистре
  (`VKScheduleParser._clear_text`): «расписаниемассовыхкатанийс15по21августа»,
  «суббота15августа» — шаблоны писать под склеенный текст.
- Период задан днями с названием месяца словом, поэтому базовый разбор периода
  (группы 2/3 в формате `dd.mm`) не подходит: переопределить ТОЛЬКО
  `_get_schedule_date_period(text, period_pattern) -> DatePeriod | None`
  (точка расширения в `VKScheduleParser`), НЕ `_get_posts_with_schedule`
  и НЕ `_get_period_date_list`.
- Разбор периода вынести в `APLArenaUtils.get_date_period(match) -> DatePeriod`;
  месяц — через `months_obj` (`src_utils/base_utils/months_obj.py`), год — текущий.
  Поддержать необязательный месяц у первой даты («с 15 по 21 августа» —
  месяц начала = месяцу конца).
- `PERIOD_PATTERN`: `расписаниемассовыхкатанийс(\d{1,2})([а-я]{3,9})?по(\d{1,2})([а-я]{3,9})`.
- Дата дня парсится через `months_obj` (день + название месяца), день недели
  в шаблоне обязателен (`[а-я]{5,11}` перед числом) — защита от ложного
  срабатывания на «21августа» внутри строки периода.
- Сеансы: интервалы `HH:MM-HH:MM`, начало сеанса — через
  `DateTimeCustomUtils.parse_hour_minute`; строки без интервала пропускать,
  None отфильтровывать (как `StachekIcebergUtils.get_sessions`).
- Исправить импорт в текущей заготовке: `from classes.schedule_parser import
  VKScheduleParser` импортирует модуль, а не класс — нужно
  `from classes.schedule_parser.VKScheduleParser import VKScheduleParser`.
- Добавить `APL_ARENA` в `classes/LocationId.py`, `classes/ArenaId.py`,
  `classes/ArenaName.py`; зарегистрировать в `main_script.py` по образцу
  `stachek_iceberg_location_parser`.
- Docstring'и и типизация — в стиле `StachekIcebergParser`.

## Контекст
- В `VKScheduleParser` выстроена цепочка: `_get_posts_with_schedule` →
  `_get_period_date_list` (строит список дат через
  `DateTimeCustomUtils.create_day_list_from_period`) →
  `_get_schedule_date_period` (парсинг границ периода, возвращает
  `DatePeriod | None`). Базовая реализация `_get_schedule_date_period`
  ожидает группы 2 и 3 шаблона как даты `dd.mm`.
- Актуальность поста: текущая дата или дата через 7 дней входит в период.
- Образец: `parsers/StachekIcebergParser.py`; разбор месяца словом —
  как в `JubiParser`/`IcePalaceParser`.
- Побочно обнаружено (вне скоупа, по согласованию): устаревший docstring у
  `_get_posts_with_schedule` (`str | None` → `List[str]`, контракт групп 2/3
  переехал в `_get_schedule_date_period`); `DateTimeCustomUtils.get_date_list`
  стал мёртвым кодом.

## Открытые вопросы
- Какой числовой id у APL Арены в бэкенде (schedule-api.fsk8.ru) для enum'ов?
  Следующий свободный — 10, но нужно реальное значение.
- Отображаемое имя арены для `ArenaName` («APL Арена»?).
- Точный формат блока дня в посте: идут ли интервалы сразу после строки даты
  или есть строка-заголовок («массовые катания:»)? От этого зависит
  `SKATING_SCHEDULE_PATTERN` (терпимый вариант с захватом до следующей даты
  обсуждался в чате).
- Начинается ли пост сразу со строки «Расписание массовых катаний...»
  (базовый фильтр использует `re.match` — якорь на начало текста)?
