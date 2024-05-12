import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .classes.day_schedule import DaySchedule
from .utils.months_obj import months_obj
from .utils.get_time_obj import get_time_obj


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


def get_jubi_day_schedule_list():
    url = 'https://www.yubi.ru/afisha/katok/'
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, 'lxml')
    data_list_raw = soup.find_all('div', class_='skat_item_cont')
    day_schedule_list = get_day_schedule_list(data_list_raw)
    return day_schedule_list


