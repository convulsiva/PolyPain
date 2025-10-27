from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import TypeVar

from ..infra.client import Client

T = TypeVar("T")


class ScrapingError(Exception):
    pass


class CallWrapABCMeta(ABCMeta):
    def __new__(mcls, name, bases, namespace, **kwargs) -> type:
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        mcls._maybe_wrap_call(cls)
        return cls

    @staticmethod
    def _maybe_wrap_call(cls: type) -> None:
        call_func = cls.__dict__.get("__call__", None)
        if call_func is None:
            return
        if getattr(call_func, "__isabstractmethod__", False):
            return
        if getattr(call_func, "__wrapped_by_meta__", False):
            return

        @wraps(call_func)
        def wrapper(*args, **kwargs):
            try:
                return call_func(*args, **kwargs)
            except Exception as err:
                raise ScrapingError(str(err)) from err

        wrapper.__wrapped_by_meta__ = True
        cls.__call__ = wrapper


class BaseScraper[T](metaclass=CallWrapABCMeta):
    def __init__(self, client: Client) -> None:
        self._client = client

    @abstractmethod
    def __call__(self, *args, **kwargs) -> T:
        raise NotImplementedError
