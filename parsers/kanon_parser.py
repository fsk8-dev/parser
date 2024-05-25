from typing import List
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from .classes.day_schedule import DaySchedule
from .utils.get_time_obj import get_time_obj
from .utils.get_time_string import get_time_string
from parsers.classes.arena_name import Arena
from parsers.classes.arena_schedule import ArenaSchedule


def get_time_list(soup: BeautifulSoup, date_list: List[datetime]):
    pattern = r'\d{2}:\d{2}'
    time_list_raw = []
    tr_list = (soup
               .find('table', class_='table-schedule')
               .find('tbody')
               .find_all('tr'))
    for _ in date_list:
        time_list_raw.append([])
    for tr in tr_list:
        td_list = tr.find_all('td')
        for index, td in enumerate(td_list):
            time_string = get_time_string(td.text.strip())
            if re.search(pattern, time_string):
                time_obj = get_time_obj(time_string, date_list[index])
                time_list_raw[index].append(time_obj)
    time_list = filter(lambda x: len(x) > 0, time_list_raw)
    return time_list


def get_date_list():
    date_list = []
    monday_date = datetime.now() - timedelta(datetime.now().weekday())
    end_date = monday_date + timedelta(6)
    current_date = monday_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list


def get_day_schedule_list(time_list: List[List[datetime]]):
    day_schedule_list = list(map(lambda x: DaySchedule(x[0], x), time_list))
    return day_schedule_list


def get_arena_schedule_list(time_list):
    arena_schedule_list = []
    day_schedule_list = get_day_schedule_list(time_list)
    arena_schedule_list.append(ArenaSchedule(Arena.GRAND_KANON, day_schedule_list))
    return arena_schedule_list


def get_kanon_schedule_list():
    url = 'https://grand-ice.ru/raspisanie'
    request = requests.get(url)
    request.encoding = 'utf-8'
    text = request.text
    soup = BeautifulSoup(text, 'lxml')
    date_list = get_date_list()
    time_list = get_time_list(soup, date_list)
    arena_schedule_list = get_arena_schedule_list(time_list)
    return arena_schedule_list




