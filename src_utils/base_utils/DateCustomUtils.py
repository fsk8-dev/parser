import re
from datetime import datetime


class DateCustomUtils:
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
        parts = time.strip().split(':')
        if len(parts) != 2:
            return None
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            return datetime(date.year, date.month, date.day, hour, minute)
        except ValueError:
            return None
