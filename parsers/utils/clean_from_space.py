def clean_from_space(text: str):
    text_clean = (text.replace(' ', '')
                    .replace(r'&nbs;', '')
                    .replace('\u00A0', '')
                    .replace('\xa0', ''))
    return text_clean


