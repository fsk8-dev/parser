from datetime import datetime


class DatePeriod:
    """
    Represents a period of time with a start and end date.

    Args:
        start (datetime): The start date of the period.
        end (datetime): The end date of the period.
    """
    def __init__(self, start: datetime, end: datetime):
        """
        Initializes a DatePeriod object with the given start and end dates.

        Args:
            start (datetime): The start date of the period.
            end (datetime): The end date of the period.
        """
        self.start = start
        self.end = end
