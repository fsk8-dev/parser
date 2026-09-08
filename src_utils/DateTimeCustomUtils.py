import re
from datetime import datetime, timedelta
from typing import List


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
    def create_day_list_from_period(period_start: datetime, period_end: datetime) -> List[datetime]:
        """
        Create a list of dates between the given period start and end dates.

        Args:
            period_start (datetime): The start date of the period.
            period_end (datetime): The end date of the period.

        Returns:
            List[datetime]: A list of dates between the period start and end dates.
        """
        day_list = []
        current_date = period_start

        # Iterate over the dates within the period
        while current_date <= period_end:
            day_list.append(current_date)
            current_date += timedelta(days=1)

        return day_list
