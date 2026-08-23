from abc import ABC
import requests
from classes.schedule_parser.BaseScheduleParser import BaseScheduleParser

class VKScheduleParser(BaseScheduleParser, ABC):

    def get_post_list(self):
        api = 'https://api.vk.com/method/wall.get'
        token = 'a0dbbc43a0dbbc43a0dbbc43a5a0b46d55aa0dba0dbbc43fe958607b4f11a2daf88c756'
        version = 5.199

        response = requests.get(
            api,
            params={
                'access_token': token,
                'v': version,
                'domain': self.url,
            }
        )
        data = response.json()['response']['items']
        return data
