from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models, transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from .managers import UserInvitationManager, UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Use the built-in user model.
    """

    username_validator = UnicodeUsernameValidator()

    first_name = models.CharField(_("voornaam"), max_length=255, blank=True)
    last_name = models.CharField(_("achternaam"), max_length=255, blank=True)
    email = models.EmailField(_("e-mailadres"), unique=True)
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

    USERNAME_FIELD = "email"

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


class UserInvitation(models.Model):
    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name="invitatie",
        verbose_name=_("user"),
    )

    key = models.CharField(
        verbose_name=_("key"), max_length=64, unique=True, default=get_random_string
    )
    accepted = models.BooleanField(verbose_name=_("accepted"), default=False)

    created = models.DateTimeField(verbose_name=_("created"), default=timezone.now)
    sent = models.DateTimeField(verbose_name=_("sent"), null=True)

    inviter = models.ForeignKey("User", null=True, blank=True, on_delete=models.CASCADE)

    objects = UserInvitationManager()

    def send_invitation(self, request, **kwargs):
        invite_url = reverse("organisaties:invitation_accept", args=[self.key])
        invite_url = request.build_absolute_uri(invite_url)
        ctx = kwargs

        ctx.update(
            {
                "invite_url": invite_url,
                "user_full_name": self.user.get_full_name(),
                "key": self.key,
                "inviter": self.inviter,
            }
        )
        subject = settings.INVITATION_SUBJECT
        email_template = settings.INVITATION_TEMPLATE
        html_message = render_to_string(email_template, context=ctx)

        send_mail(
            subject,
            strip_tags(html_message),
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            html_message=html_message,
        )

        self.sent = timezone.now()
        self.save()

    def accept_invitation(self, request, cleaned_data):
        with transaction.atomic():
            self.user.set_password(cleaned_data["password"])
            self.user.save()

            self.accepted = True
            self.save()

            messages.add_message(
                request,
                messages.SUCCESS,
                _("Uitnodiging met succes aanvaard."),
            )

    class Meta:
        verbose_name = _("user invitation")
        verbose_name_plural = _("user invitations")

    def __str__(self):
        return f"Invitation {self.user.email}"


class Role(models.Model):
    """
    A role that governs the relationship between a municipality and user.
    """

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="roles",
    )
    lokale_overheid = models.ForeignKey(
        "organisaties.LokaleOverheid",
        on_delete=models.PROTECT,
        related_name="roles",
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
        allowed_roles = [
            str(r.verbose_name) for r in self.get_roles() if getattr(self, r.name)
        ]
        return f"{self.user} @ {self.lokale_overheid.organisatie.owms_pref_label}: {', '.join(allowed_roles)}"

    def get_absolute_url(self):
        return reverse(
            "organisaties:overheid_roles", kwargs={"pk": self.lokale_overheid.pk}
        )
