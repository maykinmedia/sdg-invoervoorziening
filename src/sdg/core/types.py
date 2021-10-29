from dataclasses import dataclass

from django.core.management import call_command

from sdg.core.constants import PublicData


@dataclass
class LoadCommand:
    name: str
    source: PublicData

    def execute(self):
        """Execute the loading command using django's API."""
        call_command(self.name, self.source.value)
