import re
from datetime import datetime
from .classes.day_schedule import DaySchedule
from .utils.clean_from_space import clean_from_space
from .utils.clean_from_wierd import clean_from_wierd
from .utils.get_time_obj import get_time_obj
from .vk_utils.get_post_list import get_post_list
from .vk_utils.get_post import get_post
from .vk_utils.get_date_list import get_date_list


def get_day_schedule_list(text, sport_schedule_pattern):
    time_pattern = r'\d{2}:\d{2}-\d{2}:\d{2}'
    date_list = []
    day_schedule_list = []
    matches = re.findall(sport_schedule_pattern, text)
    if matches:
        for match in matches:
            time_list = []
            practice_date = datetime.strptime(f'{match[0]}.{datetime.now().year}', '%d.%m.%Y')
            date_list.append(practice_date)
            time_list_raw = match[1].split('\n')
            for time in time_list_raw:
                if re.search(time_pattern, time):
                    time_current_list = time.split('-')
                    time_obj = get_time_obj(time_current_list[0], practice_date)
                    time_list.append(time_obj)
            day_schedule_list.append(DaySchedule(practice_date, time_list))
    return day_schedule_list


def get_stachek_iceberg_schedule_list():
    schedule_key_word = 'Расписание сеансов'
    period_pattern = r'расписание.*?((\d{2}\.\d{2}).*?(\d{2}\.\d{2})).*(?=\n)'
    skating_schedule_pattern = r'(\d{1,2}\.\d{1,2}).*\nмассовоекатание.*\n((\d{1,2}:\d{1,2}-\d{1,2}:\d{1,2}\n){0,})'
    post_list = get_post_list('icebergkatok')
    post = get_post(post_list, schedule_key_word, period_pattern)
    day_schedule_list = get_day_schedule_list(post, skating_schedule_pattern)
    return day_schedule_list



