from abc import ABC


class OrganizationTypeConfiguration(ABC):
    """
    Base class used to configure a given organization type.
    """

    logo = None
    footer_logo = None


class MunicipalityConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for municipalities.
    """

    logo = "images/logo.png"
    footer_logo = "images/vng_logo.svg"


class ProvinceConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for provinces.
    """

    logo = "images/logo.png"
    footer_logo = "images/vng_logo.svg"


class WaterAuthorityConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for water authorities.
    """

    logo = "images/waterschaphuis_logo.png"
    footer_logo = "images/ipo_logo.png"
