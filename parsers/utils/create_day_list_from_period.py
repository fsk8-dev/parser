from datetime import datetime, timedelta


def create_day_list_from_period(period_start: datetime, period_end: datetime):
    day_list = []
    current_date = period_start
    while current_date <= period_end:
        day_list.append(current_date)
        current_date += timedelta(days=1)
    return day_list
