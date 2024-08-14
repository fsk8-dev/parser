from typing import List
import mysql.connector
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from parsers.arena_tr_parser import get_tr_schedule_list
from parsers.ice_palace_parser import get_ice_palace_schedule_list
from parsers.jubi_parser import get_jubi_schedule_list
from parsers.kanon_parser import get_kanon_schedule_list
from parsers.tavr_parser import get_tavr_schedule_list
from parsers.stachek_iceberg import get_stachek_iceberg_schedule_list
from parsers.arena_led import get_arena_led_schedule_list
from parsers.classes.arena_name import Arena


# TODO: вынести запись лога в отдельную функцию


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
    date_now = datetime.now().strftime('%d.%m.%Y %H:%M')
    sql_insert_schedule = """
    insert into CurrentSchedule (sporttype_id, arena_id, json_schedule)
    values (%s, %s, %s)
  """
    try:
        cur = conn.cursor()
        cur.execute(sql_insert_schedule, (sporttype_id, arena.value, schedule))
        conn.commit()
        print(f'Arena: {arena.name} data successfully insert')
        with open('parser.log', 'a') as file:
            file.write(f'date: {date_now} Arena: {arena.name} data successfully insert \n')
    except mysql.connector.Error as e:
        print(e)
        with open('parser.log', 'a') as file:
            file.write(f'date: {date_now}{e} \n')


def encode_to_json(schedule):
    temp_list = []
    for day_schedule in schedule:
        day_schedule.day_date = day_schedule.day_date.isoformat()
        day_schedule.day_time_list = list(map(lambda x: x.isoformat(), day_schedule.day_time_list))
        temp_list.append(day_schedule.__dict__)
    json_list = json.dumps(temp_list)
    return json_list


def insert_current_schedule(conn, get_schedule_func, sporttype_id=1):
    try:
        schedule_arena_list = get_schedule_func()
    except Exception as e:
        schedule_arena_list = None
        # TODO: добавить логирование
        print(e)
    for schedule_arena in schedule_arena_list:
        schedule = schedule_arena.arena_schedule
        arena_id = schedule_arena.arena_name
        json_schedule = encode_to_json(schedule)
        request_insert_current_schedule(conn, sporttype_id, arena_id, json_schedule)





def init():
    date_now = datetime.now().strftime('%d.%m.%Y %H:%M')
    dbname = os.getenv('SCHEDULE_DBNAME')
    user = os.getenv('SCHEDULE_USERNAME')
    password = os.getenv('SCHEDULE_PASSWORD')
    host = os.getenv('SCHEDULE_HOST')
    port = 3306
    conn = create_connection(dbname, user, password, host, port)
    if conn is not None:
        with open('parser.log', 'a') as file:
            file.write(f'=========== {date_now} =========== \n')

        insert_current_schedule(conn, get_jubi_schedule_list)
        insert_current_schedule(conn, get_arena_led_schedule_list)
        insert_current_schedule(conn, get_tavr_schedule_list)
        insert_current_schedule(conn, get_ice_palace_schedule_list)
        insert_current_schedule(conn, get_tr_schedule_list)
        insert_current_schedule(conn, get_stachek_iceberg_schedule_list)
        insert_current_schedule(conn, get_kanon_schedule_list)
        conn.close()


init()
