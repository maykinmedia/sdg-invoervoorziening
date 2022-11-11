from abc import ABC

from django.utils.translation import gettext_lazy as _


class OrganizationTypeConfiguration(ABC):
    """
    Base class used to configure a given organization type.
    """

    url: str = None
    accessibility_url: str = None
    privacy_policy_url: str = None

    overlay: str = None
    footer_logo: str = None
    color_hue = int = None

    name: str = None
    name_plural: str = None


class MunicipalityConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for municipalities.
    """

    url = "https://vng.nl"
    accessibility_url = "#"
    privacy_policy_url = "#"

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
    accessibility_url = "#"
    privacy_policy_url = "#"

    overlay = ""
    footer_logo = "images/ipo_logo.png"
    color_hue = 31

    name = _("provincie")
    name_plural = _("provincies")


class WaterauthorityConfiguration(OrganizationTypeConfiguration):
    """
    Configuration for water authorities.
    """

    url = "https://www.hetwaterschapshuis.nl/"
    accessibility_url = "#"
    privacy_policy_url = "#"

    overlay = ""
    footer_logo = "images/waterschap_logo.png"
    color_hue = 186

    name = _("waterschap")
    name_plural = _("waterschappen")
