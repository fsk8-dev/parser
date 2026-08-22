from datetime import datetime


class DatePeriod:
    """
    Represents a period of time with a start and end date.

    Args:
        period_start (datetime): The start date of the period.
        period_end (datetime): The end date of the period.
    """
    def __init__(self, period_start: datetime, period_end: datetime):
        """
        Initializes a DatePeriod object with the given start and end dates.

        Args:
            period_start (datetime): The start date of the period.
            period_end (datetime): The end date of the period.
        """
        self.period_start = period_start
        self.period_end = period_end
