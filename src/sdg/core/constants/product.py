from django.conf import settings
from django.utils.translation import gettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class TaalChoices(DjangoChoices):
    nl = ChoiceItem("nl", _("Nederlands"))
    en = ChoiceItem("en", _("Engels"))

    @classmethod
    def get_available_languages(cls):
        return list(dict(cls).keys())


class DoelgroepChoices(DjangoChoices):
    burger = ChoiceItem("eu-burger", _("EU Burger"))
    bedrijf = ChoiceItem("eu-bedrijf", _("EU Bedrijf"))


class GenericProductStatus(DjangoChoices):
    NEW = ChoiceItem("new", _("Nieuw"))
    READY_FOR_ADMIN = ChoiceItem("ready_admin", _("Gereed voor beheer"))
    READY_FOR_PUBLICATION = ChoiceItem("ready_publication", _("Gereed voor publicatie"))
    EXPIRED = ChoiceItem("expired_in_upl", _("Vervallen in de UPL"))
    EOL = ChoiceItem("eol", _("Wordt binnenkort verwijderd"))
    DELETED = ChoiceItem("deleted", _("Verwijderd"))
    MISSING = ChoiceItem("missing", _("Geen referentie producten gevonden"))

    @classmethod
    def get_cms_excluded(cls, reference=False):
        """
        Get excluded statuses for the CMS.

        - Onlt show: EXPIRED, EOL and...
            - For reference products: READY_FOR_ADMIN.
            - For specific products: READY_FOR_PUBLICATION.

        :param reference: Whether to exclude for reference products or not.
        """
        exclude = [
            cls.DELETED,
            cls.MISSING,
        ]

        if reference:
            return exclude
        else:
            return exclude + [cls.NEW, cls.READY_FOR_ADMIN]

    @classmethod
    def get_api_excluded(cls):
        """
        Get excluded statuses for the API.
        """
        """
        Get excluded statuses for the CMS.

        - For reference products: only show products that are READY_FOR_ADMIN.
        - For specific products: only show products that are READY_FOR_ADMIN as
          well. The API does not require products to have a standard text to be
          present.

        NOTE: The CMS typically only shows products that contain a
        "standard text" (ie. READY_FOR_ADMIN) but the API does not have this
        requirement.

        :param reference: Whether to exclude for reference products or not.
        """
        exclude = [
            cls.DELETED,
            cls.MISSING,
        ]

        return exclude
