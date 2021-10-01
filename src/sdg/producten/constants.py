from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class PublishChoices(DjangoChoices):
    now = ChoiceItem("now", _("Nu"))
    later = ChoiceItem("later", _("Later"))
    concept = ChoiceItem("concept", _("Concept"))
