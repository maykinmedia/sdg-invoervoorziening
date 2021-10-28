from enum import Enum
from urllib.parse import urljoin

ROOT_URL = "https://standaarden.overheid.nl"


def url(path):
    return urljoin(ROOT_URL, path)


class PublicData(Enum):
    """External data source URLs, used to load in application data."""

    GEMEENTE = url("owms/terms/Gemeente.xml")
    UPN = url("/owms/oquery/UPL-actueel.csv")
    INFORMATIEGEBIED = url("/owms/oquery/SDG-Informatiegebieden.csv")
    UPN_INFORMATIEGEBIED = url("/owms/oquery/UPL-SDG-Informatiegebied.csv")
