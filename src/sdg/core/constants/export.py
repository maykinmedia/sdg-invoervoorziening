from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class AccountStatus(TextChoices):
    empty = "", _("account status is leeg")
    logged_in = "logged in", _("heeft ingelogd")
    created = "created", _("is uitgenodigd")


class Rol(TextChoices):
    empty = "", _("rol is leeg")
    is_beheerder = "beheerder", _("beheerder")
    is_redacteur = "redacteur", _("redacteur")
    is_raadpleger = "raadpleger", _("raadpleger")


class Systeemrechten(TextChoices):
    empty = "", _("standaard")
    is_superuser = "superuser", _("superuser")
    is_staff = "staff", _("staff")
