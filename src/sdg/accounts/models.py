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
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=255, blank=True)
    last_name = models.CharField(_("last name"), max_length=255, blank=True)
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_redacteur = models.BooleanField(
        _("redacteur"),
        default=False,
        help_text=_("Designates whether this user can edit the reference texts. "),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

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
    user = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        related_name="roles",
    )
    lokale_overheid = models.ForeignKey(
        "core.LokaleOverheid",
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
            "Designates whether this is a redacteur of a specific overheidsorganisatie. "
        ),
    )

    def get_allowed_roles(self):
        return [
            f
            for f in self._meta.fields
            if f.name.startswith("is_") and getattr(self, f.name)
        ]

    def __str__(self):
        allowed_roles = [str(r.verbose_name) for r in self.get_allowed_roles()]
        return f"{self.user} @ {self.lokale_overheid.organisatie.owms_pref_label}: {', '.join(allowed_roles)}"

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lokale_overheid"],
                name="unique_user_per_lokaleoverheid",
            )
        ]
