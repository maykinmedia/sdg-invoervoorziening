import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from sdg.core.db.fields import DynamicArrayField
from sdg.core.models.validators import validate_openingstijden, validate_postcode
from sdg.organisaties.managers import LokaleOverheidManager

User = get_user_model()


class LokaleOverheid(models.Model):
    """
    Municipality
    """

    uuid = models.UUIDField(
        _("UUID"),
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_(
            "De identificatie die binnen deze API gebruikt wordt voor de resource."
        ),
    )
    contact_website = models.URLField(
        _("contact website"),
        blank=True,
        help_text=_("Website van de gemeente."),
    )
    contact_telefoonnummer = models.CharField(
        _("contact telefoonnummer"),
        max_length=20,
        blank=True,
        help_text=_("Het telefoonnummer van de gemeente."),
    )
    contact_emailadres = models.EmailField(
        _("contact emailadres"),
        max_length=254,
        blank=True,
        help_text=_("Het e-mailadres van de verantwoordelijke contactpersoon."),
    )
    ondersteunings_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.SET_NULL,
        verbose_name=_("ondersteunings organisatie"),
        help_text=_("organisatie voor ondersteuning."),
        related_name="ondersteunings",
        blank=True,
        null=True,
    )
    organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("organisatie"),
        help_text=_("De organisatie van de lokale overheid."),
        related_name="organisatie",
    )
    users = models.ManyToManyField(User, through="accounts.Role")
    automatisch_catalogus_aanmaken = models.BooleanField(
        _("Automatisch catalogus aanmaken"),
        default=True,
        help_text=_(
            "Indien aangevinkt wordt een specifieke catalogus aangemaakt voor deze lokale overheid."
        ),
    )

    objects = LokaleOverheidManager()

    def user_has_manager_role(self, user: User) -> bool:
        """:returns: Boolean indicating if the provided user has manager role for this municipality."""
        return self.roles.filter(
            user=user,
            is_beheerder=True,
        ).exists()

    class Meta:
        verbose_name = _("lokale overheid")
        verbose_name_plural = _("lokale overheden")

    def __str__(self):
        return self.organisatie.owms_pref_label

    def get_absolute_url(self):
        return reverse("organisaties:catalogi:list", kwargs={"pk": self.pk})


class BevoegdeOrganisatie(models.Model):
    """
    Authorized organization custom "through"-table. This model describes the
    relation between a LokaleOverheid and an authorized organization. The
    authorized organisation can either be an Organisation or - if it doesn't
    exist - a custom name on this relation model.
    """

    uuid = models.UUIDField(
        _("UUID"),
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_(
            "De identificatie die binnen deze API gebruikt wordt voor de resource."
        ),
    )
    naam = models.CharField(
        _("naam"),
        max_length=255,
        blank=True,
        help_text=_(
            "De naam van de bevoegde organisatie. Deze mag alleen afwijken indien er geen bekende overheidsorganisatie is."
        ),
    )
    lokale_overheid = models.ForeignKey(
        LokaleOverheid,
        on_delete=models.CASCADE,
        verbose_name=_("lokale overheid"),
        help_text=_(
            "De verantwoordelijke organisatie horend bij deze bevoegde organisatie."
        ),
        related_name="bevoegde_organisaties",
    )
    organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.SET_NULL,
        verbose_name=_("organisatie"),
        related_name="bevoegde_organisaties",
        help_text=_(
            "De bij de Rijksoverheid bekende organisatie die optreed als bevoegde organisatie."
        ),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("bevoegde organisatie")
        verbose_name_plural = _("bevoegde organisaties")

    def __str__(self):
        return self.naam

    def save(self, *args, **kwargs):
        if self.organisatie:
            self.naam = self.organisatie.owms_pref_label
        super().save(*args, **kwargs)


class Lokatie(models.Model):
    """
    Location
    """

    lokale_overheid = models.ForeignKey(
        "LokaleOverheid",
        on_delete=models.CASCADE,
        verbose_name=_("lokale overheid"),
        related_name="locaties",
    )

    naam = models.CharField(
        _("naam"),
        max_length=40,
        help_text=_("De naam van de locatie."),
    )
    straat = models.CharField(
        _("straat"),
        max_length=256,
        help_text=_("De straatnaam van de locatie."),
    )
    nummer = models.PositiveIntegerField(
        _("nummer"),
        help_text=_("Het huisnummer van de locatie."),
    )
    postcode = models.CharField(
        _("postcode"),
        validators=[validate_postcode],
        max_length=6,
        help_text=_("De postcode van de locatie."),
    )
    plaats = models.CharField(
        _("plaats"),
        max_length=256,
        help_text=_("De plaatsnaam van de locatie."),
    )
    land = models.CharField(
        _("land"),
        max_length=128,
        help_text=_("Het land van de locatie."),
    )

    maandag = DynamicArrayField(
        verbose_name=_("maandag"),
        base_field=models.CharField(
            max_length=32, validators=[validate_openingstijden]
        ),
        blank=True,
        default=list,
    )
    dinsdag = DynamicArrayField(
        verbose_name=_("dinsdag"),
        base_field=models.CharField(
            max_length=32, validators=[validate_openingstijden]
        ),
        blank=True,
        default=list,
    )
    woensdag = DynamicArrayField(
        verbose_name=_("woensdag"),
        base_field=models.CharField(
            max_length=32, validators=[validate_openingstijden]
        ),
        blank=True,
        default=list,
    )
    donderdag = DynamicArrayField(
        verbose_name=_("donderdag"),
        base_field=models.CharField(
            max_length=32, validators=[validate_openingstijden]
        ),
        blank=True,
        default=list,
    )
    vrijdag = DynamicArrayField(
        verbose_name=_("vrijdag"),
        base_field=models.CharField(
            max_length=32, validators=[validate_openingstijden]
        ),
        blank=True,
        default=list,
    )
    zaterdag = DynamicArrayField(
        verbose_name=_("zaterdag"),
        base_field=models.CharField(
            max_length=32, validators=[validate_openingstijden]
        ),
        blank=True,
        default=list,
    )
    zondag = DynamicArrayField(
        verbose_name=_("zondag"),
        base_field=models.CharField(
            max_length=32, validators=[validate_openingstijden]
        ),
        blank=True,
        default=list,
    )
    openingstijden_opmerking = models.CharField(
        _("openingstijden opmerking"),
        blank=True,
        help_text=_("Opmerking over de openingstijden."),
        max_length=255,
    )

    uuid = models.UUIDField(
        _("UUID"),
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_(
            "De identificatie die binnen deze API gebruikt wordt voor de resource."
        ),
    )

    def get_formatted_address(self):
        return f"{self.naam}\n{self.straat} {self.nummer}\n{self.postcode} {self.plaats}\n{self.land}"

    class Meta:
        verbose_name = _("locatie")
        verbose_name_plural = _("locaties")

    def __str__(self):
        return self.naam
