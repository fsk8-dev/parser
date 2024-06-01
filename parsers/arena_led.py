import re
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

from .classes.day_schedule import DaySchedule
from .utils.get_time_list import get_time_list
from .utils.format_date_period import format_date_period
from .utils.clean_from_space import clean_from_space
from .utils.create_day_list_from_period import create_day_list_from_period
from .utils.months_obj import months_obj
from .utils.days_of_week_full import days_of_week_full
from .classes.arena_name import Arena
from .classes.arena_schedule import ArenaSchedule
from .classes.date_period import DatePeriod


arena_reducer_name = {
    'расписаниелед2': Arena.ARENA_LED_2,
    'расписаниелед3': Arena.ARENA_LED_3,
    'расписаниелед4': Arena.ARENA_LED_4
}


def get_text_arena(html_arena: BeautifulSoup):
    for p in html_arena.find_all('p'):
        p.append('\n')
    for div in html_arena.find_all('div'):
        div.append('\n')
    return clean_from_space(html_arena.text.lower())


def find_out_arena_name(text_arena):
    led_2_title = r'расписаниелед2'
    led_3_title = r'расписаниелед3'
    led_4_title = r'расписаниелед4'
    name_list = [led_2_title, led_3_title, led_4_title]
    for name in name_list:
        if name in text_arena:
            return arena_reducer_name[name]
    return None


def get_date_period(text) -> Optional[DatePeriod]:
    date_period_pattern = r'((\d{2})([а-я]{1,8}.*?))по((\d{2})([а-я]{1,8}.*?))'
    match = re.search(date_period_pattern, text)
    if match:
        month_period_start = months_obj[match[3]]
        day_period_start = int(match[2])
        month_period_end = months_obj[match[6]]
        day_period_end = int(match[5])
        date_period = format_date_period(month_period_start, day_period_start, month_period_end, day_period_end)
        return date_period
    else:
        return None


def get_day_schedule_list(date_period: DatePeriod, text_arena: str):
    schedule_list = []
    day_pattern = r'([а-я]{5,11}.*\n(массовыекатания.*?\n(\d{2}.\d{2}-\d{2}.\d{2}.*\n)*))'
    time_list_pattern = r'((\d{2}.\d{2}-\d{2}.\d{2}).*\n)'

    day_list = create_day_list_from_period(date_period.period_start, date_period.period_end)
    matches = re.findall(day_pattern, text_arena)
    if matches:
        for day in day_list:
            match = next((m for m in matches if days_of_week_full[day.weekday()] in m[0]), None)
            if match:
                time_list = list(map(lambda x: x[1], re.findall(time_list_pattern, match[1])))
                time_string = ';'.join(time_list).replace('.', ':')
                time_list = get_time_list(time_string, day)
                info = DaySchedule(day, time_list)
                schedule_list.append(info)
    return schedule_list


def get_arena_schedule_list(html_list: List[BeautifulSoup]):
    arena_schedule_list = []
    for html_arena in html_list:
        text_arena = get_text_arena(html_arena)
        arena_name = find_out_arena_name(text_arena)
        date_period = get_date_period(text_arena)
        if date_period is not None:
            arena_day_schedule_list = get_day_schedule_list(date_period, text_arena)
            if arena_name is not None:
                arena_schedule = ArenaSchedule(arena_name, arena_day_schedule_list)
                arena_schedule_list.append(arena_schedule)
    return arena_schedule_list


def get_arena_led_schedule_list():
    url = 'https://www.arena-led.ru/#raspisanie'
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    text = response.text
    soup = BeautifulSoup(text,  'lxml')
    html_list = soup.find_all('div', class_='t-item t-col t-col_8 t-prefix_2')
    arena_schedule_list = get_arena_schedule_list(html_list)
    return arena_schedule_list


# note pattern for allskates and hockey ([а-я]{5,11}(\d{1,2}.\d{1,2})\n(массовыекатания:\n(\d{2}.\d{2}-\d{2}.\d{2}.*\n)*)?(часхоккея:\n(\d{2}.\d{2}-\d{2}.\d{2}.*\n)*)?)
# note pattern for day-schedule with date ([а-я]{5,11}(\d{1,2}.\d{1,2})\n(массовыекатания:\n(\d{2}.\d{2}-\d{2}.\d{2}.*\n)*)?)

