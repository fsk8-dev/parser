import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .classes.day_schedule import DaySchedule
from .utils.months_obj import months_obj
from .utils.get_time_obj import get_time_obj



def get_jubi_day_schedule_list():
    url = 'https://www.arena-led.ru/#raspisanie'
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, 'lxml')
    data_list_raw = soup.find_all('div', class_='skat_item_cont')
    day_schedule_list = get_day_schedule_list(data_list_raw)
    return day_schedule_list
