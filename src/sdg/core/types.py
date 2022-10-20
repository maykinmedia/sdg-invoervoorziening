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


class EventMeta(type):
    def __getattr__(self, item):
        if hasattr(self.result, item):
            return getattr(self.result, item)
        return getattr(self, item)


class Event(metaclass=EventMeta):
    """A default event used to provide information about actions happening throughout the application."""

    class result(Enum):
        """An enum representing all the possible event results."""

        CREATE = "create"
        READ = "read"
        UPDATE = "update"
        DELETE = "delete"

    _template = "admin/core/logger/event.html"

    def __init__(self, request, instance: Model, result: result):
        self._request = request
        self._instance = instance

        self.name = instance.__class__.__name__
        self.object_name = str(instance)
        self.result = result.value
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
    def create_and_log(cls, request, instance: Model, result: result, error=None):
        event = cls(request, instance, result)
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
