import re
from datetime import datetime, timedelta


class DateTimeCustomUtils:
    @staticmethod
    def parse_day_month(date: str) -> datetime:
        day, month = map(int, date.split('.'))  # "17.08"
        year = datetime.now().year
        if month < datetime.now().month:
            year += 1
        return datetime(year, month, day)

    @staticmethod
    def find_day_month_by_digits(date: str) -> str | None:
        pattern = r'(\d{1,2})\.(\d{1,2})'
        match = re.match(pattern, date)
        return match[0] if match else None

    @staticmethod
    def parse_hour_minute(time: str, date: datetime) -> datetime | None:
        """
        This function takes a time string and a date object as input and returns a datetime object.
        If the time string is not in the format 'HH:MM', it returns None.

        Args:
            time_string (str): The time string in the format 'HH:MM'.
            date_obj (datetime): The date object to which the time will be added.

        Returns:
            datetime or None: The datetime object with the time added to the date, or None if the time string is not in the correct format.
        """
        parts = time.strip().split(':')
        if len(parts) != 2:
            return None
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            return datetime(date.year, date.month, date.day, hour, minute)
        except ValueError:
            return None

    @staticmethod
    def get_date_list(text: str, period_pattern: str):
        date_list = []
        current_year = str(datetime.now().year)
        format_pattern = '%d.%m.%Y'
        match = re.search(period_pattern, text, re.IGNORECASE)
        if match:
            start_date = datetime.strptime(f'{match.group(2)}.{current_year}', format_pattern)
            if match.group(3):
                end_date = datetime.strptime(match.group(3) + '.' + current_year, format_pattern)
            else:
                end_date = start_date
            current_date = start_date
            while current_date <= end_date:
                date_list.append(current_date)
                current_date += timedelta(days=1)
        return date_list
