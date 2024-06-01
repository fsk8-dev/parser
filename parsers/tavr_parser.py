import re
import requests
from bs4 import BeautifulSoup
from .classes.day_schedule import DaySchedule
from .utils.get_time_obj import get_time_obj
from .utils.get_time_string import get_time_string
from parsers.classes.arena_name import Arena
from parsers.classes.arena_schedule import ArenaSchedule
from .utils.clean_from_space import clean_from_space
from .utils.clean_from_row import clean_from_row
from .utils.get_date_period import get_date_period
from parsers.utils.get_date_list import get_date_list


def get_time_list(schedule_table, date_list):
    pattern = r'\d{2}:\d{2}'
    time_list_raw = []
    tr_list = schedule_table.find_all('tr')
    for _ in date_list:
        time_list_raw.append([])
    for tr in tr_list[4:]:
        td_list = tr.find_all('td')
        for index, td in enumerate(td_list):
            time_string = get_time_string(td.text.strip())
            if re.search(pattern, time_string):
                time_obj = get_time_obj(time_string, date_list[index])
                time_list_raw[index].append(time_obj)
    time_list = list(filter(lambda x: len(x) > 0, time_list_raw))
    return time_list


def get_day_schedule_list(time_list):
    day_schedule_list = list(map(lambda x: DaySchedule(x[0], x), time_list))
    return day_schedule_list


def get_arena_schedule_list(time_list):
    arena_schedule_list = []
    day_schedule_list = get_day_schedule_list(time_list)
    arena_schedule_list.append(ArenaSchedule(Arena.TAVR, day_schedule_list))
    return arena_schedule_list


def get_date_period_local(schedule_table):
    td_date = schedule_table.find('td', {'colspan': '7', 'style': 'text-align: center;'})
    td_text = td_date.text
    date_string = clean_from_space(clean_from_row(td_text.replace('Расписание катаний', '')))
    date_period = get_date_period(date_string)
    return date_period


def get_tavr_schedule_list():
    url = 'http://www.tavrsad.com/index.php?s=19'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    schedule_table = soup.body.find('table',  height="290", width="700")
    date_period = get_date_period_local(schedule_table)
    if date_period:
        date_list = get_date_list(date_period['period_start'], date_period['period_end'])
        time_list = get_time_list(schedule_table, date_list)
        arena_schedule_list = get_arena_schedule_list(time_list)
    else:
        arena_schedule_list = get_arena_schedule_list([])
    return arena_schedule_list
