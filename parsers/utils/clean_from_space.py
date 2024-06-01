def clean_from_space(text: str) -> str:
    """
    Remove whitespace characters (spaces, non-breaking spaces, and other Unicode spaces) from the given text.

    Args:
        text (str): The input text.

    Returns:
        str: The cleaned text.

    """
    # Remove spaces
    text_clean = text.replace(' ', '')

    # Remove non-breaking spaces
    text_clean = text_clean.replace(r'&nbs;', '')

    # Remove Unicode spaces
    text_clean = text_clean.replace('\u00A0', '')
    text_clean = text_clean.replace('\xa0', '')
    text_clean = text_clean.replace('\t', '')

    return text_clean
