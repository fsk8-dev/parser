import re
from datetime import datetime
from classes.DaySchedule import DaySchedule
from src_utils.base_utils import get_time_obj
from src_utils.vk_utils import get_post_list, get_post
from classes import ArenaName
from classes.ArenaSchedule import ArenaSchedule
from classes import LocationId
from classes.ArenaId import ArenaId
from classes import ScheduleType


def get_day_schedule_list(text, sport_schedule_pattern):
    time_pattern = r'\d{1,2}:\d{2}-\d{1,2}:\d{2}'
    date_list = []
    day_schedule_list = []
    matches = re.findall(sport_schedule_pattern, text)
    print('matches: ', matches)
    if matches:
        for match in matches:
            print(
                'match: ',
                match)
            time_list = []
            practice_date = datetime.strptime(f'{match[0]}.{datetime.now().year}', '%d.%m.%Y')
            print('practice_date: ', practice_date)
            date_list.append(practice_date)
            time_list_raw = match[1].split('\n')
            print('time_list_raw: ', time_list_raw)
            for time in time_list_raw:
                print('time: ', time)
                print('re.search(time_pattern, time): ', re.search(time_pattern, time))
                if re.search(time_pattern, time):
                    time_current_list = time.split('-')
                    time_obj = get_time_obj(time_current_list[0], practice_date)
                    time_list.append(time_obj)
            day_schedule_list.append(DaySchedule(practice_date, time_list))
    return day_schedule_list


def get_arena_schedule_list(post, skating_schedule_pattern):
    arena_schedule_list = []
    if post is not None:
        day_schedule_list = get_day_schedule_list(post, skating_schedule_pattern)
    else:
        day_schedule_list = []
    arena_schedule = ArenaSchedule(LocationId.STACHEK_ICEBERG, ArenaName.STACHEK_ICEBERG, ArenaId.STACHEK_ICEBERG, ScheduleType.ICE_SKATING, day_schedule_list)
    arena_schedule_list.append(arena_schedule)
    return arena_schedule_list


def get_stachek_iceberg_schedule_list():
    period_pattern = r'расписание.*?((\d{2}\.\d{2}).*?(\d{2}\.\d{2})).*(?=\n)'
    skating_schedule_pattern = r'(\d{1,2}\.\d{1,2}).*\nмассовоекатание.*\n((\d{1,2}:\d{1,2}-\d{1,2}:\d{1,2}\n){0,})'
    post_list = get_post_list('icebergkatok')
    post = get_post(post_list, period_pattern)
    arena_schedule_list = get_arena_schedule_list(post, skating_schedule_pattern)
    print(arena_schedule_list)
    return arena_schedule_list



