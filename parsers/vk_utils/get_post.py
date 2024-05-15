from typing import List
import re
from datetime import datetime, timedelta
from ..classes.day_schedule import DaySchedule
from ..utils.weekdays_obj import weekdays
from ..utils.get_time_list import get_time_list
from ..utils.clean_from_space import clean_from_space
from ..utils.clean_from_wierd import clean_from_wierd
from .get_date_list import get_date_list


def get_post(post_list, schedule_key_word, period_pattern):
    date_format = '%d.%m.%Y'
    date_now = datetime.now().strftime(date_format)
    date_now = datetime.strptime(date_now, date_format)
    filtered = filter(lambda x: schedule_key_word in x['text'], post_list)
    post_list_filtered = list(filtered)
    for post in post_list_filtered:
        text = clean_from_space(post['text'])
        text = clean_from_wierd(text)
        text = text.lower()
        date_list = get_date_list(text, period_pattern)
        # NOTE здесь можно отфильтровать расписание на будущую неделю
        if date_now in date_list:
            # TODO возвращать text
            return post
