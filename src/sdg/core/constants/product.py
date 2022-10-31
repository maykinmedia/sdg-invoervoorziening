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
