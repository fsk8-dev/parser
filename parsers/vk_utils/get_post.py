from typing import List
import re
from datetime import datetime, timedelta
from ..utils.clean_from_space import clean_from_space
from ..utils.clean_from_wierd import clean_from_wierd
from .get_date_list import get_date_list


def clear_text(text):
    text = clean_from_space(text)
    text = clean_from_wierd(text)
    text = text.lower()
    return text


def get_post(post_list, schedule_key_word, period_pattern):
    date_format = '%d.%m.%Y'
    date_now = datetime.now().strftime(date_format)
    date_now = datetime.strptime(date_now, date_format)
    post_list_text = list(map(lambda x: clear_text(x['text']), post_list))
    post_list_filtered = list(filter(lambda x: re.match(period_pattern, x), post_list_text))
    for post in post_list_filtered:
        date_list = get_date_list(post, period_pattern)
        # NOTE здесь можно отфильтровать расписание на будущую неделю
        if date_now in date_list:
            # TODO возвращать text
            return post
