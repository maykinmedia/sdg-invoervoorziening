from abc import ABC

from django.utils.translation import gettext_lazy as _


class OrganizationTypeConfiguration(ABC):
    """
    Base class used to configure a given organization type.
    """

    url: str = ""
    accessibility_url: str = ""
    privacy_policy_url: str = ""

    footer_logo: str = ""

    name: str = ""
    name_plural: str = ""


class MunicipalityConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for municipalities.
    """

    url = "https://vng.nl"

    footer_logo = "images/vng_logo.svg"

    name = _("gemeente")
    name_plural = _("gemeenten")


class ProvinceConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for provinces.
    """

    url = "https://www.ipo.nl/"

    footer_logo = "images/ipo_logo.png"

    name = _("provincie")
    name_plural = _("provincies")


class WaterauthorityConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for water authorities.
    """

    url = "https://www.hetwaterschapshuis.nl/"

    footer_logo = "images/waterschap_logo.png"

    name = _("waterschap")
    name_plural = _("waterschappen")
