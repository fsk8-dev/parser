from datetime import datetime
from ..classes.date_period import DatePeriod


def format_date_period(month_period_start: int, day_period_start: int, month_period_end: int, day_period_end: int) -> DatePeriod:
    """
    Calculate the start and end dates of a period based on the current year and the given inputs.

    Args:
        month_period_start (int): The start month of the period.
        day_period_start (int): The start day of the period.
        month_period_end (int): The end month of the period.
        day_period_end (int): The end day of the period.

    Returns:
        DatePeriod: A DatePeriod object with the start and end dates of the period.
    """
    # Check if the period spans across the year boundary
    if month_period_start == 12 and month_period_end == 1:
        year_period_end = datetime.now().year + 1  # If so, calculate the end year
    else:
        year_period_end = datetime.now().year  # Otherwise, use the current year

    # Calculate the start date of the period
    period_start = datetime(datetime.now().year, month_period_start, day_period_start)

    # Calculate the end date of the period
    period_end = datetime(year_period_end, month_period_end, day_period_end)

    # Create a DatePeriod object with the start and end dates
    date_period = DatePeriod(period_start, period_end)
    return date_period
