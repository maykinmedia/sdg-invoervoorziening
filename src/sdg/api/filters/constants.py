from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class ProductAanwezigChoices(DjangoChoices):
    ja = ChoiceItem("ja", _("Ja"), boolean=True)
    nee = ChoiceItem("nee", _("Nee"), boolean=False)
    onbekend = ChoiceItem("onbekend", _("Onbekend"), boolean=None)
