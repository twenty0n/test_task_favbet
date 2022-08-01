from typing import Dict

from .types import Result

__all__ = ['CustomCodeException', 'EventsNotFounded', 'FilterOutData']


class CustomCodeException(Exception):
    pass


class EventsNotFounded(Exception):
    pass


class FilterOutData:

    @staticmethod
    def __check_data_for_correcting(data: Dict) -> list[Dict]:
        if data.get("events", None):
            return data['events']
        else:
            raise EventsNotFounded("Events not found")

    @staticmethod
    def __filter_data(data: list[Dict]) -> list[Result]:
        return list(event
                    for event in map(lambda x: Result(**{key: value
                                                         for key, value in x.items()
                                                         if key in Result.__match_args__}), data)
                    if '–' in event.name)

    def __new__(cls, *args, **kwargs) -> list[Result]:
        return cls.__filter_data(cls.__check_data_for_correcting(kwargs['data']))
