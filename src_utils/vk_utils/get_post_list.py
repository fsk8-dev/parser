import requests


def get_post_list(domain: str):
    API = 'https://api.vk.com/method/wall.get'
    token = 'a0dbbc43a0dbbc43a0dbbc43a5a0b46d55aa0dba0dbbc43fe958607b4f11a2daf88c756'
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
