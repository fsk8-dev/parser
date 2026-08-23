import os
import unittest
from datetime import datetime
from unittest import mock

from classes.ArenaId import ArenaId
from classes.ArenaName import ArenaName
from classes.LocationId import LocationId
from classes.LocationParser import LocationParser
from classes.schedule_parser.VKScheduleParser import VKScheduleParser
from parsers.StachekIcebergParser import StachekIcebergParser, StachekIcebergUtils


class ConcreteVKParser(VKScheduleParser):
    """Минимальная конкретная реализация VKScheduleParser для тестов."""

    url = 'testcommunity'

    def get_day_schedule_list(self):
        return []


POST_TEXT = (
    'расписаниес18.08по24.08\n'
    '18.08пн\n'
    'массовоекатание\n'
    '10:00-12:00\n'
    '14:00-16:00\n'
    '19.08вт\n'
    'массовоекатание\n'
    '11:00-13:00\n'
)


def make_parser() -> StachekIcebergParser:
    return StachekIcebergParser(StachekIcebergUtils(), token='test-token')


class StachekIcebergParserTestCase(unittest.TestCase):
    def test_get_day_schedule_list_happy_path(self):
        parser = make_parser()
        with mock.patch.object(parser, '_get_post', return_value=POST_TEXT):
            day_schedule_list = parser.get_day_schedule_list()

        year = datetime.now().year
        self.assertEqual(len(day_schedule_list), 2)

        first_day = day_schedule_list[0]
        self.assertEqual(first_day.day_date, datetime(year, 8, 18))
        self.assertEqual(
            first_day.day_time_list,
            [datetime(year, 8, 18, 10, 0), datetime(year, 8, 18, 14, 0)],
        )

        second_day = day_schedule_list[1]
        self.assertEqual(second_day.day_date, datetime(year, 8, 19))
        self.assertEqual(second_day.day_time_list, [datetime(year, 8, 19, 11, 0)])

    def test_get_day_schedule_list_without_post_returns_empty_list(self):
        parser = make_parser()
        with mock.patch.object(parser, '_get_post', return_value=None):
            self.assertEqual(parser.get_day_schedule_list(), [])

    def test_location_parser_returns_arena_schedule_with_empty_session_list(self):
        parser = make_parser()
        location_parser = LocationParser(
            location_id=LocationId.STACHEK_ICEBERG,
            arena_name=ArenaName.STACHEK_ICEBERG,
            arena_id=ArenaId.STACHEK_ICEBERG,
            parser=parser,
        )
        with mock.patch.object(parser, '_get_post', return_value=None):
            arena_schedule_list = location_parser.get_schedule()

        self.assertEqual(len(arena_schedule_list), 1)
        self.assertEqual(arena_schedule_list[0].sessionList, [])

    def test_unparsed_time_is_filtered_out(self):
        date = datetime(datetime.now().year, 8, 18)
        time_list = StachekIcebergUtils.get_sessions(
            ['10:00:30-12:00', '11:00-13:00'],
            date,
        )
        self.assertEqual(time_list, [datetime(date.year, 8, 18, 11, 0)])


class VKScheduleParserTestCase(unittest.TestCase):
    def test_get_post_list_raises_value_error_on_api_error(self):
        parser = ConcreteVKParser(token='test-token')
        response = mock.Mock()
        response.json.return_value = {'error': {'error_msg': 'Access denied'}}
        with mock.patch('requests.get', return_value=response):
            with self.assertRaises(ValueError):
                parser._get_post_list()

    def test_token_is_required_without_env(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(KeyError):
                ConcreteVKParser()

    def test_explicit_token_bypasses_env(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            parser = ConcreteVKParser(token='test-token')
        self.assertEqual(parser.token, 'test-token')


if __name__ == '__main__':
    unittest.main()
