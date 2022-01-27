import abc
from collections import defaultdict
from typing import Dict

events = defaultdict(list)


class EventFunction(abc.ABC):
    exception_messages = {
        "default": None,
        "admin": None,
    }

    @abc.abstractmethod
    def __call__(self, user, request):
        raise NotImplementedError

    def get_message(self, message_type):
        return self.exception_messages[message_type]


def post_event(event_name: str, **kwargs) -> Dict[EventFunction, Exception]:
    errors = {}

    for fn in events[event_name]:
        try:
            fn(**kwargs)
        except Exception as e:
            errors[fn] = e

    return errors


def add_event(event_name: str, function: EventFunction):
    events[event_name].append(function)
