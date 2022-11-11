import importlib
from enum import Enum

from django.core.exceptions import ImproperlyConfigured

CONFIG_MODULE = "sdg.conf.types.organization"


def _get_config_map():
    """
    Initialize the configuration map from the `types.organization` module.
    """
    result = {}

    module = importlib.import_module(CONFIG_MODULE)

    for org_type in OrganizationType:
        name = org_type.title()
        class_name = f"{name}Configuration"

        if not hasattr(module, class_name):
            raise ImproperlyConfigured(
                f"{class_name} missing for {org_type}. Please add it to: {CONFIG_MODULE}"
            )

        config_class = getattr(module, class_name)
        result[org_type] = config_class()

    return result


class OrganizationType(str, Enum):
    """
    Available organization types.

    Parts of the application are customized depending on this configuration.
    """

    MUNICIPALITY = "municipality"
    PROVINCE = "province"
    WATER_AUTHORITY = "waterauthority"

    @classmethod
    def from_string(cls, value):
        value = value.lower()

        if value not in list(cls):
            raise ImproperlyConfigured(
                f"SDG_ORGANIZATION_TYPE must be one of: {', '.join(OrganizationType)}"
            )

        return cls(value)

    @property
    def config(self):
        return _config_map.get(self)


_config_map = _get_config_map()
