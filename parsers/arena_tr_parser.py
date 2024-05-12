from typing import List
import re
import requests
from datetime import datetime, timedelta
from .classes.day_schedule import DaySchedule
from .utils.weekdays_obj import weekdays
from .utils.get_time_list import get_time_list
from .utils.clean_from_space import clean_from_space
from .utils.clean_from_wierd import clean_from_wierd


class Schedule:
    def __init__(self, figure_skating, hockey):
        self.figure_skating = figure_skating
        self.hockey = hockey


def get_post_list():
    API = 'https://api.vk.com/method/wall.get'
    token = 'a0dbbc43a0dbbc43a0dbbc43a5a0b46d55aa0dba0dbbc43fe958607b4f11a2daf88c756'
    version = 5.199
    domain = 'arena_tr'

    response = requests.get(
        API,
        params={
            'access_token': token,
            'v': version,
            'domain': domain
        }
    )
    data = response.json()['response']['items']
    return data


def get_post(post_list):
    date_format = '%d.%m.%Y'
    date_now = datetime.now().strftime(date_format)
    date_now = datetime.strptime(date_now, date_format)
    filtered = filter(lambda x: 'Массовое катание' in x['text'], post_list)
    post_list_filtered = list(filtered)
    for post in post_list_filtered:
        text = clean_from_space(post['text'])
        text = clean_from_wierd(text)
        text = text.lower()
        date_list = get_date_list(text)
        # NOTE здесь можно отфильтровать расписание на будущую неделю
        if date_now in date_list:
            # TODO возвращать text
            return post


def get_date_list(text: str):
    date_list = []
    current_year = str(datetime.now().year)
    format_pattern = '%d.%m.%Y'
    period_pattern = r'расписание.*((\d{2}\.\d{2})-(\d{2}\.\d{2})).*(?=\n)'
    match = re.search(period_pattern, text)
    if match:
        end_date = datetime.strptime(match.group(3) + '.' + current_year, format_pattern)
        start_date = datetime.strptime(f'{match.group(2)}.{end_date.year}', format_pattern)
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
    return date_list


def get_clean_list(string):
    schedule_string = re.sub(r'[^\w\s :;.,-]', '',
                             string.replace('\n', ';')
                             .replace('; ;', ';')
                             .replace('.', ''))
    temp_list = list(filter(lambda x: x != '', schedule_string.split(';')))
    clean_list = list(map(lambda x: x.replace(',', ';'), temp_list))
    return clean_list


def get_practice_date(date_list, match):
    weekday_name = match.group(1).lower()
    weekday_number = weekdays[weekday_name]
    practice_date_list = list(filter(lambda x: x.weekday() == weekday_number, date_list))
    practice_date = practice_date_list[0] if len(practice_date_list) > 0 else None
    return practice_date


def get_hockey_string(text):
    string = text.split('Час Хоккея')[-1]
    return string


def get_skating_string(text):
    string = text.split('массовоекатание')[-1].split('часхоккея')[0]
    return string


def get_time_list_all(string, date_list):
    time_list_all = []
    week_day_group_pattern = r'^\s*(\w{2}):'
    week_day_compile = re.compile(week_day_group_pattern)
    clean_list = get_clean_list(string)
    for item in clean_list:
        match = re.search(week_day_group_pattern, item)
        if match:
            practice_date = get_practice_date(date_list, match)
            if practice_date is not None:
                all_times_string = re.sub(week_day_compile, '', item)
                time_list = get_time_list(all_times_string, practice_date)
                time_list_all.append(time_list)
    return time_list_all


def get_day_schedule_list(sport_string: str, date_list: List[datetime]):
    time_list_all = get_time_list_all(sport_string, date_list)
    day_schedule_list = list(map(lambda x: DaySchedule(x[0], x), time_list_all))
    return day_schedule_list


def get_tr_day_schedule_list():
    post_list = get_post_list()
    post = get_post(post_list)
    if post is not None:
        text = clean_from_space(post['text'])
        text = clean_from_wierd(text)
        text = text.lower()
        date_list = get_date_list(text)
        skating_string = get_skating_string(text)
        day_schedule_list = get_day_schedule_list(skating_string, date_list)
        return day_schedule_list
    else:
        return None

# ([а-яА-Я]{2}):(\d{1,2}:\d{2}-\d{1,2}:\d{2}[.,\n\r])*
