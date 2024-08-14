import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .classes.day_schedule import DaySchedule
from .classes.arena_id import ArenaId
from .classes.schedule_type import ScheduleType
from .utils.months_obj import months_obj
from .utils.get_time_obj import get_time_obj
from parsers.classes.arena_name import Arena
from parsers.classes.arena_schedule import ArenaSchedule


def get_date(data):
    date_raw = data.find('div', class_='date')
    date_list = date_raw.string.lower().split(' ')
    month_name = date_list[1]
    month = months_obj[month_name]
    day = int(date_list[0])
    date_object = datetime(datetime.now().year, month, day)
    return date_object


def get_time_list(data, date_obj):
    time_list = []
    time_section_raw = data.find('div', class_='time_cont')
    time_list_raw = time_section_raw.find_all('a')
    for time_raw in time_list_raw:
        time_obj = get_time_obj(time_raw.string, date_obj)
        if time_obj is not None:
            time_list.append(time_obj)
    return time_list


def get_day_schedule_list(data_list):
    day_schedule_list = []
    for data in data_list:
        date_obj = get_date(data)
        time_list = get_time_list(data, date_obj)
        day_schedule = DaySchedule(date_obj, time_list)
        day_schedule_list.append(day_schedule)
    return day_schedule_list


def get_arena_schedule_list(data_list):
    arena_schedule_list = []
    day_schedule_list = get_day_schedule_list(data_list)
    arena_schedule_list.append(ArenaSchedule(Arena.JUBI_BASE, ArenaId.JUBI_BASE, ScheduleType.ICE_SKATING, day_schedule_list))
    return arena_schedule_list


def get_jubi_schedule_list():
    url = 'https://www.yubi.ru/afisha/katok/'
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, 'lxml')
    data_list_raw = soup.find_all('div', class_='skat_item_cont')
    arena_schedule_list = get_arena_schedule_list(data_list_raw)
    return arena_schedule_list


