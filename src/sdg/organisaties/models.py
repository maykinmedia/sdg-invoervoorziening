from typing import List

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from sdg.core.db.fields import DynamicArrayField
from sdg.core.models import ProductenCatalogus
from sdg.core.models.mixins import ContactgegevensMixin
from sdg.core.models.validators import validate_openingstijden, validate_postcode

User = get_user_model()


class LokaleOverheid(ContactgegevensMixin, models.Model):
    """
    Municipality
    """

    ondersteunings_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("ondersteunings organisatie"),
        help_text=_("organisatie voor ondersteuning."),
        related_name="ondersteunings",
    )
    verantwoordelijke_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("verantwoordelijke organisatie"),
        help_text=_("Organisatie verantwoordelijk voor de decentrale informatie."),
        related_name="verantwoordelijke",
    )
    bevoegde_organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("bevoegde organisatie"),
        help_text=_("Bevoegd gezag verantwoordelijk voor de procedure."),
        related_name="bevoegde",
    )
    organisatie = models.ForeignKey(
        "core.Overheidsorganisatie",
        on_delete=models.CASCADE,
        verbose_name=_("organisatie"),
        help_text=_("De organisatie van de lokale overheid."),
        related_name="organisatie",
    )
    users = models.ManyToManyField(User, through="accounts.Role")

    def create_specific_catalogs(self) -> List[ProductenCatalogus]:
        """Create a specific catalog (if it doesn't exist) for each reference catalog."""

        catalogus_list = []
        for catalog in ProductenCatalogus.objects.filter(is_referentie_catalogus=True):
            catalogus_list.append(
                ProductenCatalogus(
                    referentie_catalogus=catalog,
                    lokale_overheid=self,
                    is_referentie_catalogus=False,
                    domein=catalog.domein,
                    versie=catalog.versie,
                    naam=f"{str(self)} ({catalog.naam})",
                )
            )
        return ProductenCatalogus.objects.bulk_create(
            catalogus_list, ignore_conflicts=True
        )

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
        return reverse("organisaties:overheid_detail", kwargs={"pk": self.pk})


class Lokatie(models.Model):
    """
    Location
    """

    lokale_overheid = models.ForeignKey(
        "LokaleOverheid",
        on_delete=models.CASCADE,
        verbose_name=_("lokale overheid"),
        related_name="lokaties",
    )

    naam = models.CharField(
        _("naam"),
        max_length=40,
        help_text=_("De naam van de lokatie."),
    )
    straat = models.CharField(
        _("straat"),
        max_length=256,
    )
    nummer = models.PositiveIntegerField(
        _("nummer"),
    )
    postcode = models.CharField(
        _("postcode"),
        validators=[validate_postcode],
        max_length=6,
    )
    plaats = models.CharField(
        _("plaats"),
        max_length=256,
    )
    land = models.CharField(
        _("land"),
        max_length=128,
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

    def get_formatted_address(self):
        return f"{self.naam}\n{self.straat} {self.nummer}\n{self.postcode} {self.plaats}\n{self.land}"

    class Meta:
        verbose_name = _("lokatie")
        verbose_name_plural = _("lokaties")

    def __str__(self):
        return self.naam
