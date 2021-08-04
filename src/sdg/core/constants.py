from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class TaalChoices(DjangoChoices):
    nl = ChoiceItem("NL", _("Nederlands"))
    en = ChoiceItem("EN", _("Engels"))


class DoelgroepChoices(DjangoChoices):
    burgers = ChoiceItem("burgers", _("Burgers"))
    bedrijven = ChoiceItem("bedrijven", _("Bedrijven"))
