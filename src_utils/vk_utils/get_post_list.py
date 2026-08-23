import requests


def get_post_list(domain: str):
    API = 'https://api.vk.com/method/wall.get'
    token = ''
    version = 5.199

    response = requests.get(
        API,
        params={
            'access_token': token,
            'v': version,
            'domain': domain,
        }
    )
    data = response.json()['response']['items']
    return data
