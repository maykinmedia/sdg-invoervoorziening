from enum import Enum
from functools import partial
from types import DynamicClassAttribute
from urllib.parse import urljoin

root_url = partial(urljoin, base="https://standaarden.overheid.nl")


class PublicData(Enum):
    """External data source URLs, used to load in application data."""

    GOVERNMENT_ORGANISATION = "owms/terms/Overheidsorganisatie.xml"
    MUNICIPALITY = "owms/terms/Gemeente.xml"
    UPN = "owms/oquery/UPL-actueel.csv"
    INFORMATIEGEBIED = "owms/oquery/SDG-Informatiegebieden.csv"
    UPN_INFORMATIEGEBIED = "owms/oquery/UPL-SDG-Informatiegebied.csv"

    @DynamicClassAttribute
    def value(self):
        return root_url(url=self._value_)
