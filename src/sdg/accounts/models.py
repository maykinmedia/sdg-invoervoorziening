from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Use the built-in user model.
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("gebruikersnaam"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("Een gebruiker met die gebruikersnaam bestaat al."),
        },
    )
    first_name = models.CharField(_("voornaam"), max_length=255, blank=True)
    last_name = models.CharField(_("achternaam"), max_length=255, blank=True)
    email = models.EmailField(_("e-mailadres"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Geeft aan of de gebruiker kan inloggen op deze beheerdersite."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Geeft aan of deze gebruiker als actief moet worden behandeld. Deselecteer dit in plaats van accounts te "
            "verwijderen."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("gebruiker")
        verbose_name_plural = _("gebruikers")

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name


class Role(models.Model):
    """
    A role that governs the relationship between a municipality and user.
    """

    user = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        related_name="roles",
    )
    lokale_overheid = models.ForeignKey(
        "organisaties.LokaleOverheid",
        on_delete=models.PROTECT,
        related_name="lokale_overheden",
    )

    is_beheerder = models.BooleanField(
        _("beheerder"),
        default=False,
        help_text=_(
            "Designates whether this user is a manager of a specific overheidsorganisatie. "
        ),
    )
    is_redacteur = models.BooleanField(
        _("redacteur"),
        default=False,
        help_text=_(
            "Designates whether this is an editor of a specific overheidsorganisatie. "
        ),
    )

    def get_catalogs(self, reference=None):
        if reference is not None:
            return self.lokale_overheid.catalogi.filter(
                is_referentie_catalogus=reference
            ).all()
        return self.lokale_overheid.catalogi.all()

    @classmethod
    def get_roles(cls):
        return [
            f
            for f in cls._meta.fields
            if f.name.startswith("is_") and getattr(cls, f.name)
        ]

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lokale_overheid"],
                name="unique_user_per_lokaleoverheid",
            )
        ]

    def __str__(self):
        allowed_roles = [str(r.verbose_name) for r in self.get_roles()]
        return f"{self.user} @ {self.lokale_overheid.organisatie.owms_pref_label}: {', '.join(allowed_roles)}"
