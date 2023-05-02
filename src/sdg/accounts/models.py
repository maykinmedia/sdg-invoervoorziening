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
from django.utils.translation import gettext_lazy as _

from allauth.account.models import EmailAddress
from djchoices import ChoiceItem, DjangoChoices

from sdg.conf.utils import org_type_cfg

from .managers import UserInvitationManager, UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Use the built-in user model.
    """

    username_validator = UnicodeUsernameValidator()

    first_name = models.CharField(_("voornaam"), max_length=255)
    last_name = models.CharField(_("achternaam"), max_length=255)
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
        ordering = ("first_name", "last_name")

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def __str__(self):
        return self.get_full_name() or self.email


class UserInvitation(models.Model):
    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name="invitatie",
        verbose_name=_("gebruiker"),
    )

    key = models.CharField(
        verbose_name=_("key"), max_length=64, unique=True, default=get_random_string
    )
    accepted = models.BooleanField(verbose_name=_("geaccepteerd"), default=False)

    created = models.DateTimeField(verbose_name=_("aangemaakt"), default=timezone.now)
    sent = models.DateTimeField(verbose_name=_("verzonden"), null=True)

    inviter = models.ForeignKey("User", null=True, blank=True, on_delete=models.CASCADE)

    objects = UserInvitationManager()

    def send_invitation(self, request, **kwargs):
        invite_url = reverse("invitation_accept", args=[self.key])
        invite_url = request.build_absolute_uri(invite_url)
        ctx = kwargs

        cfg = org_type_cfg()
        ctx.update(
            {
                "org_name": cfg.organisation_name,
                "org_type_name": cfg.name,
                "org_type_name_plural": cfg.name_plural,
                "org_type_email": cfg.email,
                "more_info_url": cfg.more_info_url,
                "invite_url": invite_url,
                "user_full_name": self.user.get_full_name(),
                "key": self.key,
                "inviter": self.inviter,
                "products_disabled": settings.SDG_CMS_PRODUCTS_DISABLED,
            }
        )
        subject = settings.INVITATION_SUBJECT.format(
            org_type_name_plural=cfg.name_plural
        )
        html_message = render_to_string(settings.INVITATION_TEMPLATE, context=ctx)

        send_mail(
            subject,
            strip_tags(html_message),
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            html_message=html_message,
        )

        self.sent = timezone.now()
        self.save()

    def accept_invitation(self, request, password):
        with transaction.atomic():
            self.user.set_password(password)
            self.user.save()

            self.accepted = True
            self.save()

            self.verify_email()

            messages.add_message(
                request,
                messages.SUCCESS,
                _("Uitnodiging met succes aanvaard."),
            )

    def verify_email(self):
        return EmailAddress.objects.create(
            email=self.user.email,
            user=self.user,
            verified=True,
            primary=True,
        )

    class Meta:
        verbose_name = _("uitnodiging")
        verbose_name_plural = _("uitnodigingen")

    def __str__(self):
        return f"Invitation {self.user.email}"


class Role(models.Model):
    """
    A role that governs the relationship between a municipality and user.
    """

    class choices(DjangoChoices):
        """All possible role choices for a municipality and user."""

        MANAGER = ChoiceItem("is_beheerder", label=_("Beheerder"))
        EDITOR = ChoiceItem("is_redacteur", label=_("Redacteur"))
        CONSULTANT = ChoiceItem("is_raadpleger", label=_("Raadpleger"))

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

    ontvangt_mail = models.BooleanField(
        _("ontvangt e-mails"),
        default=False,
        help_text=_(
            "Designates whether this user receives emails on product changes for this organisation."
        ),
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
    is_raadpleger = models.BooleanField(
        _("raadpleger"),
        default=False,
        help_text=_(
            "Designates whether this user is a consultant of a specific overheidsorganisatie. "
        ),
    )

    class Meta:
        verbose_name = _("rol")
        verbose_name_plural = _("rollen")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lokale_overheid"],
                name="unique_user_per_lokaleoverheid",
            )
        ]

    def __str__(self):
        return f"{self.user} — {self.lokale_overheid.organisatie.owms_pref_label}"

    def get_absolute_url(self):
        return reverse(
            "organisaties:roles:list", kwargs={"pk": self.lokale_overheid.pk}
        )
