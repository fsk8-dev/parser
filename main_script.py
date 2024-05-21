from typing import List
import mysql.connector
import json
import os
from dotenv import load_dotenv
from parsers.arena_tr_parser import get_tr_day_schedule_list
from parsers.ice_palace_parser import get_ice_palace_day_schedule_list
from parsers.jubi_parser import get_jubi_day_schedule_list
from parsers.kanon_parser import get_kanon_day_schedule_list
from parsers.tavr_parser import get_tavr_day_schedule_list
from parsers.stachek_iceberg import get_stachek_iceberg_schedule_list
from parsers.arena_led_2 import get_arena_led_2_day_schedule_list
from enum import Enum


class Arena(Enum):
    TR = 1
    JUBI_BASE = 8
    TAVR = 5
    ICE_PALACE = 6
    GRAND_KANON = 7
    STACHEK_ICEBERG = 9
    ARENA_LED_2 = 10
    ARENA_LED_3 = 11
    ARENA_LED_4 = 12


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def create_connection(dbname, user, password, host, port):
    conn = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=dbname,
            port=port
        )
        print('Connection successful')
    except mysql.connector.Error as e:
        print(e)
    return conn


def request_insert_current_schedule(conn, sporttype_id: int, arena: Arena, schedule: str):
    sql_insert_schedule = """
    insert into CurrentSchedule (sporttype_id, arena_id, json_schedule)
    values (%s, %s, %s)
  """
    try:
        cur = conn.cursor()
        cur.execute(sql_insert_schedule, (sporttype_id, arena.value, schedule))
        conn.commit()
        print(f'Arena: {arena.name} data successfully insert')
    except mysql.connector.Error as e:
        print(e)


def encode_to_json(schedule):
    temp_list = []
    for day_schedule in schedule:
        day_schedule.day_date = day_schedule.day_date.isoformat()
        day_schedule.day_time_list = list(map(lambda x: x.isoformat(), day_schedule.day_time_list))
        temp_list.append(day_schedule.__dict__)
    json_list = json.dumps(temp_list)
    return json_list


def insert_current_schedule(conn, get_schedule_func, arena_id, sporttype_id=1):
    schedule = get_schedule_func()
    json_schedule = encode_to_json(schedule)
    request_insert_current_schedule(conn, sporttype_id, arena_id, json_schedule)


def init():
    dbname = os.getenv('SCHEDULE_DBNAME')
    user = os.getenv('SCHEDULE_USERNAME')
    password = os.getenv('SCHEDULE_PASSWORD')
    host = os.getenv('SCHEDULE_HOST')
    port = 3306
    conn = create_connection(dbname, user, password, host, port)
    if conn is not None:
        insert_current_schedule(conn, get_arena_led_2_day_schedule_list, Arena.ARENA_LED_2)
        insert_current_schedule(conn, get_stachek_iceberg_schedule_list, Arena.STACHEK_ICEBERG)
        insert_current_schedule(conn, get_tr_day_schedule_list, Arena.TR)
        insert_current_schedule(conn, get_ice_palace_day_schedule_list, Arena.ICE_PALACE)
        insert_current_schedule(conn, get_jubi_day_schedule_list, Arena.JUBI_BASE)
        insert_current_schedule(conn, get_kanon_day_schedule_list, Arena.GRAND_KANON)
        insert_current_schedule(conn, get_tavr_day_schedule_list, Arena.TAVR)
        conn.close()


init()
