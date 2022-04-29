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
