from pathlib import Path
from typing import Dict, Literal, Union

from django.utils.translation import gettext_lazy as _

import yaml
from pydantic import BaseModel, Field, HttpUrl, validator

EmptyUrl = Literal["#"]


class OrganizationTypeConfiguration(BaseModel):
    """
    Base class used to configure an organization type.
    """

    url: Union[HttpUrl, EmptyUrl]
    accessibility_url: Union[HttpUrl, EmptyUrl]
    privacy_policy_url: Union[HttpUrl, EmptyUrl]

    overlay: str
    footer_logo: str
    color_hue: int = Field(gte=0, lte=360)

    name: str
    name_plural: str

    @validator("name", "name_plural")
    def i18n(cls, value):
        return _(value)


def _load_organization_types() -> Dict[str, OrganizationTypeConfiguration]:
    """
    Dynamically load the organization types from ``conf.organizations``
    """
    result = {}

    conf_path = Path(__file__).parent.parent
    for conf in (conf_path / "organizations").glob("*.yml"):
        with open(conf) as f:
            data = yaml.safe_load(f)
            result[conf.stem] = OrganizationTypeConfiguration(**data)

    return result


organization_types = _load_organization_types()
