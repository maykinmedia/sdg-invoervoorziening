from enum import Enum

from sdg.conf.organization_types import (
    MunicipalityConfiguration,
    ProvinceConfiguration,
    WaterAuthorityConfiguration,
)


class OrganizationType(str, Enum):
    """
    Available organization types.

    Parts of the application are customized depending on this configuration.
    """

    MUNICIPALITY = "MUNICIPALITY"
    PROVINCE = "PROVINCE"
    WATER_AUTHORITY = "WATER_AUTHORITY"

    @property
    def config(self):
        _config_map.get(self)


_config_map = {
    OrganizationType.MUNICIPALITY: MunicipalityConfiguration,
    OrganizationType.PROVINCE: ProvinceConfiguration,
    OrganizationType.WATER_AUTHORITY: WaterAuthorityConfiguration,
}
