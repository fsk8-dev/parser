import re


def clean_from_wierd(text):
    clean_text = re.sub(r'[^\w\s\d\n\r-.,;:?!]', '', text)
    return clean_text
