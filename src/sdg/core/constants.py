from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class TaalChoices(DjangoChoices):
    nl = ChoiceItem("NL", _("Nederlands"))
    en = ChoiceItem("EN", _("Engels"))

    @classmethod
    def get_available_languages(cls):
        return dict(cls).keys()


class DoelgroepChoices(DjangoChoices):
    burgers = ChoiceItem("burgers", _("Burgers"))
    bedrijven = ChoiceItem("bedrijven", _("Bedrijven"))
