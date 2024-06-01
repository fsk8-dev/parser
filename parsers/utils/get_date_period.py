import re
from datetime import datetime
from .months_obj import months_obj


def get_date_period(text):
    """
    Extracts the start and end dates from a given text string.

    Args:
        text (str): The text string to extract dates from.

    Returns:
        dict: A dictionary containing the start and end dates.
              If no dates are found, both 'period_start' and 'period_end' are set to None.
    """
    date_period = {'period_start': None, 'period_end': None}

    # Regular expression pattern to match the date format
    period_pattern = r'((\d{1,2})([а-я]{1,8}.*?))по((\d{1,2})([а-я]{1,8}.*?))'
    test = text
    # Search for the pattern in the text
    match = re.search(period_pattern, text)

    # If a match is found, extract the start and end dates
    if match:
        if months_obj[match[3]] == 12 and months_obj[match[6]] == 1:
            year_period_end = datetime.now().year + 1
        else:
            year_period_end = datetime.now().year
        # Get the start date
        date_period['period_start'] = datetime(datetime.now().year, months_obj[match[3]], int(match[2]))

        # Get the end date
        date_period['period_end'] = datetime(year_period_end, months_obj[match[6]], int(match[5]))

    else:
        date_period = None
    return date_period
