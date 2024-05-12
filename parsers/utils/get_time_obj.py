from datetime import datetime


def get_time_obj(time_string: str, date_obj: datetime):
    time_list = time_string.split(':')
    if len(time_list) == 2:
        hour = int(time_list[0])
        minute = int(time_list[1])
        time_obj = datetime(date_obj.year, date_obj.month, date_obj.day, hour, minute)
        return time_obj
    else:
        return None
