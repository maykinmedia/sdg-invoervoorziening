from django.utils.translation import gettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class PublishChoices(DjangoChoices):
    date = ChoiceItem("date", _("Opslaan en publiceren"))
    concept = ChoiceItem("concept", _("Opslaan als concept"))
