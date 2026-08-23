from dotenv import load_dotenv
load_dotenv()

import requests

from classes import ArenaSchedule

from parsers.kanon_parser import get_kanon_schedule_list
from parsers.tavr_parser import get_tavr_schedule_list
from parsers.arena_led import get_arena_led_schedule_list

from parsers.JubiParser import create_jubi_location_parser
jubi_location_parser = create_jubi_location_parser()
from parsers.TaurideParser import create_tauride_location_parser
tauride_location_parser = create_tauride_location_parser()
from parsers.IcePalaceParser import create_ice_palace_location_parser
ice_palace_location_parser = create_ice_palace_location_parser()
from parsers.MagnitParser import create_magnit_arena_location_parser
magnit_arena_location_parser = create_magnit_arena_location_parser()
from parsers.StachekIcebergParser import create_stachek_iceberg_location_parser
stachek_iceberg_location_parser = create_stachek_iceberg_location_parser()


# TODO: вынести запись лога в отдельную функцию


def send_schedule(location_id: int, arena_schedule: dict):
    url = 'https://schedule-api.fsk8.ru/api/location-schedules/update'
    payload = arena_schedule
    response = requests.post(f'{url}/{location_id}',  json=payload)
    #  TODO: добавить логирование


def format_arena_schedule(arena_schedule: ArenaSchedule):
    arena_schedule.sessionList = list(map(lambda x: {"startDate": x.startDate.isoformat()}, arena_schedule.sessionList))
    return arena_schedule.__dict__


def handle_schedule(get_schedule_func):
    try:
        arena_schedule_list = get_schedule_func()
        print('arena_schedule_list: ', arena_schedule_list)
    except Exception as e:
        arena_schedule_list = []
        # TODO: добавить логирование
        print(e)
    for arena_schedule in arena_schedule_list:
        json_schedule = format_arena_schedule(arena_schedule)
        send_schedule(arena_schedule.locationId, json_schedule)


def init():
    handle_schedule(stachek_iceberg_location_parser.get_schedule)
    handle_schedule(magnit_arena_location_parser.get_schedule)
    handle_schedule(ice_palace_location_parser.get_schedule)
    handle_schedule(tauride_location_parser.get_schedule)
    handle_schedule(jubi_location_parser.get_schedule)
    handle_schedule(get_kanon_schedule_list)
    handle_schedule(get_tavr_schedule_list)
    handle_schedule(get_arena_led_schedule_list)


init()

