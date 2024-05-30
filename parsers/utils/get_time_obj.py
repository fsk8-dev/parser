from datetime import datetime


def get_time_obj(time_string: str, date_obj: datetime) -> datetime or None:
    """
    This function takes a time string and a date object as input and returns a datetime object.
    If the time string is not in the format 'HH:MM', it returns None.

    Args:
        time_string (str): The time string in the format 'HH:MM'.
        date_obj (datetime): The date object to which the time will be added.

    Returns:
        datetime or None: The datetime object with the time added to the date, or None if the time string is not in the correct format.
    """
    # Split the time string into hours and minutes
    time_list = time_string.split(':')

    # Check if the time string is in the correct format
    if len(time_list) == 2:
        hour = int(time_list[0])
        minute = int(time_list[1])

        # Create a datetime object with the time added to the date
        time_obj = datetime(date_obj.year, date_obj.month, date_obj.day, hour, minute)

        return time_obj
    else:
        return None
