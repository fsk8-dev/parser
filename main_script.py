import requests

from parsers.classes.arena_schedule import ArenaSchedule
from parsers.arena_tr_parser import get_tr_schedule_list
from parsers.ice_palace_parser import get_ice_palace_schedule_list
from parsers.jubi_parser import get_jubi_schedule_list
from parsers.kanon_parser import get_kanon_schedule_list
from parsers.tavr_parser import get_tavr_schedule_list
from parsers.stachek_iceberg import get_stachek_iceberg_schedule_list
from parsers.arena_led import get_arena_led_schedule_list


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
    except Exception as e:
        arena_schedule_list = []
        # TODO: добавить логирование
        print(e)
    for arena_schedule in arena_schedule_list:
        json_schedule = format_arena_schedule(arena_schedule)
        send_schedule(arena_schedule.locationId, json_schedule)


def init():
    handle_schedule(get_arena_led_schedule_list)
    handle_schedule(get_stachek_iceberg_schedule_list)
    handle_schedule(get_kanon_schedule_list)
    handle_schedule(get_ice_palace_schedule_list)
    handle_schedule(get_tavr_schedule_list)
    handle_schedule(get_jubi_schedule_list)
    handle_schedule(get_tr_schedule_list)


init()

