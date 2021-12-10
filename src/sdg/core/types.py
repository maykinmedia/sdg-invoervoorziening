from dataclasses import dataclass
from enum import Enum

from django.core.management import call_command
from django.db.models import Model

from sdg.core.constants import PublicData


@dataclass
class LoadCommand:
    name: str
    source: PublicData

    def execute(self):
        """Execute the loading command using django's API."""
        call_command(self.name, self.source.value)


class Event:
    """A default event used to provide information about actions happening throughout the application."""

    class _action(Enum):
        """An enum representing the different actions that can be performed."""

        START = "start"
        SKIP = "skip"
        SUCCESS = "success"
        FAILURE = "failure"

    START, SKIP, SUCCESS, FAILURE = (
        _action.START,
        _action.SKIP,
        _action.SUCCESS,
        _action.FAILURE,
    )

    name: str
    method: str
    view: dict
    params: dict
    payload: dict
    headers: dict

    _template = "core/logger/event.html"

    def __init__(self, request, instance: Model, action: _action):
        self._request = request
        self._instance = instance

        self.name = self.__class__.__name__
        self.action = action.value
        self.method = request.method
        self.params = dict(request.GET)
        self.payload = dict(request.POST)
        self.headers = dict(request.headers)
        self.view = {
            "name": self._request.resolver_match.view_name,
            "path": self._request.resolver_match._func_path,
        }

    @property
    def data(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    @classmethod
    def create_and_log(cls, request, instance: Model, action: _action, error=None):
        event = cls(request, instance, action)
        return event.log(error=error)

    def log(self, error: Exception = None):
        from timeline_logger.models import TimelineLog

        _data = self.data
        if error:
            _data.update({"error": str(error)})

        return TimelineLog.log_from_request(
            self._request,
            self._instance,
            self._template,
            **_data,
        )
