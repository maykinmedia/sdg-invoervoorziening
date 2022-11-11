from abc import ABC

from django.utils.translation import gettext_lazy as _


class OrganizationTypeConfiguration(ABC):
    """
    Base class used to configure a given organization type.
    """

    url: str = ""
    accessibility_url: str = ""
    privacy_policy_url: str = ""

    overlay = str = ""
    footer_logo: str = ""

    name: str = ""
    name_plural: str = ""


class MunicipalityConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for municipalities.
    """

    url = "https://vng.nl"

    overlay = "images/gemeentes.png"
    footer_logo = "images/vng_logo.svg"
    color_hue = 202

    name = _("gemeente")
    name_plural = _("gemeenten")


class ProvinceConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for provinces.
    """

    url = "https://www.ipo.nl/"

    footer_logo = "images/ipo_logo.png"
    color_hue = 31

    name = _("provincie")
    name_plural = _("provincies")


class WaterauthorityConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for water authorities.
    """

    url = "https://www.hetwaterschapshuis.nl/"

    overlay = ""
    footer_logo = "images/waterschap_logo.png"
    color_hue = 186

    name = _("waterschap")
    name_plural = _("waterschappen")
