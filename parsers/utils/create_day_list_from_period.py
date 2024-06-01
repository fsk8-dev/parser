from datetime import datetime, timedelta
from typing import List


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
