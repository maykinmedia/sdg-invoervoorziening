import abc
from collections import UserDict, defaultdict
from typing import Callable

from django.contrib import messages

event_register = defaultdict(list)


class CustomMessageEvent(abc.ABC):
    default_message: str = None
    admin_message: str = None

    @abc.abstractmethod
    def __call__(self, user, request):
        raise NotImplementedError


class ErrorDict(UserDict):
    DEFAULT = "default"
    ADMIN = "admin"

    def add_messages(self, request, message_type=DEFAULT):
        for function, exception in self.items():
            message = getattr(function, f"{message_type}_message", exception)
            messages.add_message(request, messages.ERROR, message)


def post_event(event_name: str, **kwargs) -> ErrorDict:
    errors = ErrorDict()

    for function in event_register[event_name]:
        try:
            function(**kwargs)
        except Exception as e:
            errors[function] = e

    return errors


def add_event(event_name: str, function: Callable):
    event_register[event_name].append(function)
