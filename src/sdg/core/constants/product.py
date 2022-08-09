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


class ProductStatus(DjangoChoices):
    NEW = ChoiceItem("nieuw", _("Nieuw"))
    MONITOR = ChoiceItem("gereed-voor-beheer", _("Gereed voor beheer"))
    PUBLICATE = ChoiceItem("gereed-voor-publicatie", _("Gereed voor publicatie"))
    EXPIRED = ChoiceItem("vervallen-in-de-upl", _("Vervallen in de UPL"))
    EOL = ChoiceItem("eol", _("End of life"))
    DELETED = ChoiceItem("verwijdert", _("Verwijdert"))
    MISSING = ChoiceItem(
        "geen-product-gevonden", _("Geen referentie producten gevonden")
    )
