def get_time_string(time_string_raw):
    time_list = time_string_raw.split('-')
    time_string = time_list[0] if len(time_list) > 0 else None
    return time_string
