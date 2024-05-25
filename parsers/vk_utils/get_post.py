from typing import List, Optional
import re
from datetime import datetime, timedelta
from ..utils.clean_from_space import clean_from_space
from ..utils.clean_from_wierd import clean_from_wierd
from .get_date_list import get_date_list


def clear_text(text):
    text = clean_from_space(text)
    text = clean_from_wierd(text)
    text = text.lower()
    return text


def get_post(post_list: List[dict], period_pattern: str) -> Optional[str]:
    """
    Get the first post from the given post list that matches the schedule keyword and period pattern,
    and whose date list contains the current date.

    Args:
        post_list (List[dict]): The list of posts to search through.
        period_pattern (str): The pattern to match against the post text to extract the date range.

    Returns:
        Optional[str]: The text of the matching post, or None if no match is found.
    """
    date_format = '%d.%m.%Y'
    date_now = datetime.now().strftime(date_format)
    date_now = datetime.strptime(date_now, date_format)

    # Clear the text of each post and filter out posts that don't match the period pattern
    post_list_text = list(map(lambda x: clear_text(x['text']), post_list))
    post_list_filtered = list(filter(lambda x: re.match(period_pattern, x), post_list_text))

    for post in post_list_filtered:
        date_list = get_date_list(post, period_pattern)
        # NOTE: You can filter the schedule for the upcoming week here if needed
        if date_now in date_list:
            # TODO: Return the text of the matching post
            return post

    return None
