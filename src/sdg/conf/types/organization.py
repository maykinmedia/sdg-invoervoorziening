from pathlib import Path
from typing import Literal, Union

from django.utils.translation import gettext_lazy as _

import yaml
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator

from sdg.conf.types.exceptions import OrganizationTypeException

EmptyUrl = Literal["#"]


class OrganizationTypeConfiguration(BaseModel):
    """
    Base class used to configure an organization type.
    """

    url: Union[HttpUrl, EmptyUrl]
    accessibility_url: Union[HttpUrl, EmptyUrl]
    privacy_policy_url: Union[HttpUrl, EmptyUrl]
    email: EmailStr

    overlay: str
    overlay_size: str
    footer_logo: str
    color_hue: int = Field(gte=0, lte=360)

    name: str
    name_plural: str

    @validator("overlay", "footer_logo")
    def static_file(cls, value):
        from django.contrib.staticfiles import finders

        if value and not finders.find(value):
            raise OrganizationTypeException("Static file does not exist.")

        return value

    @validator("name", "name_plural")
    def i18n(cls, value):
        return _(value)


def _load_type_map() -> dict:
    """
    Load the organization type map from available types.
    """
    result = {}

    conf_path = Path(__file__).parent.parent
    for conf in (conf_path / "organizations").glob("*.yml"):
        with open(conf) as f:
            data = yaml.safe_load(f)
            result[conf.stem] = data

    return result


available_org_types = _load_type_map()
