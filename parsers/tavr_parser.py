import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .classes.day_schedule import DaySchedule
from .utils.get_time_obj import get_time_obj
from .utils.get_time_string import get_time_string
from parsers.classes.arena_name import Arena
from parsers.classes.arena_schedule import ArenaSchedule


def get_date_list(schedule_table):
    date_list = []
    tr_list = schedule_table.find_all('tr')
    if len(tr_list) > 2:
        td_list = tr_list[2].find_all('td')
        for td in td_list:
            date_string = td.text.strip()
            # TODO переделать, чтобы не было ошибки в с случае если новый год наступает в середине недели
            try:
                date = datetime.strptime(f'{date_string}.{datetime.now().year}', '%d.%m.%Y')
                date_list.append(date)
            except Exception as e:
                date_list.append(datetime(1, 1, 1))
                print(e)  # TODO записать в лог
    return date_list


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


def get_tavr_schedule_list():
    url = 'http://www.tavrsad.com/index.php?s=19'
    response = requests.get(url)
    html_text = response.text
    soup = BeautifulSoup(html_text, 'html.parser')
    schedule_table = soup.body.find('table',  height="290", width="700")
    date_list = get_date_list(schedule_table)
    time_list = get_time_list(schedule_table, date_list)
    arena_schedule_list = get_arena_schedule_list(time_list)
    return arena_schedule_list



