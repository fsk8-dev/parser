from datetime import datetime, timedelta


def get_date_list(period_start: datetime, period_end: datetime):
    date_list = []
    current_date = period_start
    while current_date <= period_end:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list
