from typing import List
import re
from datetime import datetime, timedelta
from .classes.day_schedule import DaySchedule
from .utils.weekdays_obj import weekdays
from .utils.get_time_list import get_time_list
from parsers.vk_utils.get_post_list import get_post_list
from parsers.vk_utils.get_post import get_post
from parsers.vk_utils.get_date_list import get_date_list
from parsers.classes.arena_name import Arena
from parsers.classes.arena_schedule import ArenaSchedule


class Schedule:
    def __init__(self, figure_skating, hockey):
        self.figure_skating = figure_skating
        self.hockey = hockey


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
    week_day_compile = re.compile(week_day_group_pattern, )
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
    day_schedule_list = list(map(lambda x: DaySchedule(x[0].replace(hour=0, minute=0), x), time_list_all))
    return day_schedule_list


def get_arena_schedule_list(post, period_pattern):
    arena_schedule_list = []
    if post is not None:
        date_list = get_date_list(post, period_pattern)
        skating_string = get_skating_string(post)
        day_schedule_list = get_day_schedule_list(skating_string, date_list)
    else:
        day_schedule_list = []
    arena_schedule = ArenaSchedule(Arena.TR, day_schedule_list)
    arena_schedule_list.append(arena_schedule)
    return arena_schedule_list


def get_tr_schedule_list():
    period_pattern = r'(расписание.*((\d{2}\.\d{2})-(\d{2}\.\d{2})).*(?=\n))|расписание.*?(\d{2}\.\d{2})'
    post_list = get_post_list('arena_tr')
    post = get_post(post_list, period_pattern)
    arena_schedule_list = get_arena_schedule_list(post, period_pattern)
    return arena_schedule_list


# ([а-яА-Я]{2}):(\d{1,2}:\d{2}-\d{1,2}:\d{2}[.,\n\r])*
