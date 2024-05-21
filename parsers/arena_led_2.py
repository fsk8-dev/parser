from typing import List
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .classes.day_schedule import DaySchedule
from .utils.months_obj import months_obj
from .utils.get_time_obj import get_time_obj


def get_day_schedule_list(html_list: List[BeautifulSoup]):
    for html_arena in html_list:
        text_arena = html_arena.text.lower()
        test = 0
    return 0


def get_arena_led_2_day_schedule_list():
    url = 'https://www.arena-led.ru/#raspisanie'
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    text = response.text
    soup = BeautifulSoup(text,  'lxml')
    html_list = soup.find_all('div', class_='t-item t-col t-col_8 t-prefix_2')
    day_schedule_list = get_day_schedule_list(html_list)
    return day_schedule_list
