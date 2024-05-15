import re
from datetime import datetime, timedelta


def get_date_list(text: str, period_pattern: str):
    date_list = []
    current_year = str(datetime.now().year)
    format_pattern = '%d.%m.%Y'
    match = re.search(period_pattern, text)
    if match:
        end_date = datetime.strptime(match.group(3) + '.' + current_year, format_pattern)
        start_date = datetime.strptime(f'{match.group(2)}.{end_date.year}', format_pattern)
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
    return date_list


