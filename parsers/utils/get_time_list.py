from .get_time_obj import get_time_obj


def get_time_list(all_times_string: str, date_obj):
    time_list_all = []
    temp_list = all_times_string.split(';')
    for item in temp_list:
        if item != '':
            time_string = item.split('-')[0].strip()
            time_iso = get_time_obj(time_string, date_obj)
            if time_iso is not None:
                time_list_all.append(time_iso)
    return time_list_all
