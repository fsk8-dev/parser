from datetime import datetime
from .utils.clean_from_space import clean_from_space
from .utils.clean_from_wierd import clean_from_wierd
from parsers.vk_utils.get_post_list import get_post_list
from parsers.vk_utils.get_post import get_post


def get_stachek_iceberg_schedule_list():
    schedule_key_word = 'Расписание сеансов'
    period_pattern = r'расписание.*?((\d{2}\.\d{2}).*?(\d{2}\.\d{2})).*(?=\n)'
    post_list = get_post_list('icebergkatok')
    post = get_post(post_list, schedule_key_word, period_pattern)
    return post



