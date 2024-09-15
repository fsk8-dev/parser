from typing import List
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from .classes.day_schedule import DaySchedule

from parsers.classes.arena_name import ArenaName
from parsers.classes.arena_schedule import ArenaSchedule
from .classes.location_id import LocationId
from .classes.arena_id import ArenaId
from .classes.schedule_type import ScheduleType

from .utils.months_obj import months_obj
from .utils.get_time_list import get_time_list
from .utils.clean_from_space import clean_from_space



def get_data_list(soup):
    data_list = []
    text = clean_from_space(soup.text)
    pattern = r'((\d{1,2}-)?\d{1,2}[а-яА-Я]{3,9}:(\d{1,2}\s*:\s*\d{2}-\d{1,2}\s*:\s*\d{2}\s*;)*).*?'
    matches = re.findall(pattern, text)
    for match in matches:
        item = match[0]
        data_list.append(item)
    return data_list


def is_date_period(string: str):
    pattern = r'\d{1,2}\s*-\s*\d{1,2}\s*[а-я]{1,8}'
    if re.search(pattern, string):
        return True
    else:
        return False


def get_temp_day_list(date_string: str):
    temp_day_list = []
    temp_list = date_string.replace('-', '').replace(r'\s+|\xa0', ' ').split(' ')
    for item in temp_list:
        if item != '':
            temp_day_list.append(item)
    return temp_day_list


def get_day_list_from_date_period(date_string):
    day_list = []
    temp_list = get_temp_day_list(date_string)
    if len(temp_list) == 3:
        month = months_obj[temp_list[2]]
        for day in range(int(temp_list[0]), int(temp_list[1]) + 1):
            day_list.append(datetime(datetime.now().year, month, day))
    return day_list


def get_date(date_temp: str):
    temp_list = date_temp.split(' ')
    if len(temp_list) == 2:
        return datetime(datetime.now().year, int(months_obj[temp_list[1]]),  int(temp_list[0]))
    else:
        return None


def get_day_schedule_list(data_list: List[str]):
    schedule_list = []
    pattern = r'(.*?)([а-яА-Я]+)'
    for data in data_list:
        temp_list = data.split(':', 1)
        if len(temp_list) == 2:
            date_temp = temp_list[0].strip()
            matches = re.findall(pattern, date_temp)
            date_temp = ' '.join([matches[0][0], matches[0][1]])
            if is_date_period(date_temp):
                day_list = get_day_list_from_date_period(date_temp)
                for day in day_list:
                    time_list = get_time_list(temp_list[1].strip(), day)
                    info = DaySchedule(day, time_list)
                    schedule_list.append(info)
            else:
                day = get_date(date_temp)
                if day is not None:
                    time_list = get_time_list(temp_list[1].strip(), day)
                    info = DaySchedule(day, time_list)
                    schedule_list.append(info)
    return schedule_list


def get_arena_schedule_list(data_list: List[str]):
    arena_schedule_list = []
    day_schedule_list = get_day_schedule_list(data_list)
    arena_schedule_list.append(ArenaSchedule(LocationId.ICE_PALACE, ArenaName.ICE_PALACE, ArenaId.ICE_PALACE, ScheduleType.ICE_SKATING, day_schedule_list))
    return arena_schedule_list


def get_ice_palace_schedule_list():
    url = 'https://newarena.spb.ru/rink/'
    request = requests.get(url)
    text = request.text
    soup = BeautifulSoup(text, 'lxml')
    data_list = get_data_list(soup)
    arena_schedule_list = get_arena_schedule_list(data_list)
    return arena_schedule_list





