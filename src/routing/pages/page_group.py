# Ill admit this is bad for pages which share ALOT of functionality with minor changes
from functools import partial
from typing import Callable, Dict, Any, Tuple


class PageGroup:
    @classmethod
    def add_routes(cls):
        raise NotImplementedError

    @classmethod
    def initialize(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_route_func(cls, func: Callable[[Any, Any], Tuple[bytes, int, Dict[str, str]]]):
        return partial(func)

    @classmethod
    def as_route_func(cls, func: Callable[[Any, Any], Tuple[bytes, int, Dict[str, str]]]):
        return partial(func)

    @staticmethod
    def to_get_string(**kwargs):
        listed = []
        for k, v in kwargs.items():
            listed.append(f"{k}={v}")
        if len(listed) == 0:
            return ""
        return "?" + "&".join(listed)
