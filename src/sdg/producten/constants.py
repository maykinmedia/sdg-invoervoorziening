from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class PublishChoices(DjangoChoices):
    now = ChoiceItem("now", _("Publiceer direct"))
    later = ChoiceItem("later", _("Kies datum"))
    concept = ChoiceItem("concept", _("Opslaan als concept"))
