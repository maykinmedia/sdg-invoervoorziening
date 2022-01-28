import abc
from collections import UserDict, defaultdict

from django.contrib import messages

events = defaultdict(list)


class EventFunction(abc.ABC):
    exception_messages = {}

    @abc.abstractmethod
    def __call__(self, user, request):
        raise NotImplementedError

    def get_message(self, message_type, default=None):
        return self.exception_messages.get(message_type, default)


class ErrorDict(UserDict):
    def add_messages(self, request, message_type="default"):
        for function, exception in self.items():
            messages.add_message(
                request, messages.ERROR, function.get_message(message_type, exception)
            )


def post_event(event_name: str, **kwargs) -> ErrorDict:
    errors = ErrorDict()

    for fn in events[event_name]:
        try:
            fn(**kwargs)
        except Exception as e:
            errors[fn] = e

    return errors


def add_event(event_name: str, function: EventFunction):
    events[event_name].append(function)
