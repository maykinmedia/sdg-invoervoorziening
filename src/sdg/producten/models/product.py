from __future__ import annotations

import datetime
import uuid
from functools import partialmethod
from typing import Any, List, Optional

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import BooleanField, Case, Q, Value, When
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices

from sdg.core.constants import DoelgroepChoices
from sdg.core.constants.product import GenericProductStatus, TaalChoices
from sdg.core.utils import get_from_cache
from sdg.producten.models import (
    LocalizedGeneriekProduct,
    LocalizedProduct,
    ProductFieldMixin,
)
from sdg.producten.models.managers import (
    GeneriekProductQuerySet,
    ProductQuerySet,
    ProductVersieQuerySet,
)
from sdg.producten.types import Language
from sdg.producten.utils import build_url_kwargs, is_past_date

User = get_user_model()


class GeneriekProductOverheidsorganisatieRol(models.Model):
    generiek_product = models.ForeignKey(
        "producten.GeneriekProduct", on_delete=models.CASCADE
    )
    overheidsorganisatie = models.ForeignKey(
        "core.Overheidsorganisatie", on_delete=models.CASCADE
    )
    rol = models.CharField(_("rol"), max_length=100, blank=True)


class GeneriekProduct(models.Model):
    """
    Generic product

    Container for localized generic products holding only the properties that
    are the same for every localized generic product.
    """

    upn = models.ForeignKey(
        "core.UniformeProductnaam",
        on_delete=models.PROTECT,
        related_name="generieke_producten",
        help_text=_("De uniforme productnaam met betrekking tot dit product."),
    )
    verantwoordelijke_organisaties = models.ManyToManyField(
        "core.Overheidsorganisatie",
        through="producten.GeneriekProductOverheidsorganisatieRol",
        verbose_name=_("verantwoordelijke organisaties"),
        help_text=_("Organisaties verantwoordelijk voor de landelijke informatie"),
        blank=True,
    )
    verplicht_product = models.BooleanField(
        _("verplicht product"),
        help_text=_(
            "Geeft aan of decentrale overheden verplicht zijn informatie over dit product te leveren."
        ),
        default=False,
    )
    doelgroep = models.CharField(
        max_length=32,
        choices=DoelgroepChoices.choices,
        blank=True,
        help_text=_(
            "Geeft aan voor welke doelgroep het product is bedoeld: burgers, bedrijven of burgers en bedrijven. Wordt "
            "gebruikt wanneer een portaal informatie over het product ophaalt uit de invoervoorziening. Zo krijgen de "
            "ondernemersportalen de ondernemersvariant en de burgerportalen de burgervariant. "
        ),
    )
    eind_datum = models.DateField(
        _("Eind datum"),
        help_text=_("De datum wanneer het product komt te vervallen."),
        blank=True,
        null=True,
    )
    product_status = models.CharField(
        max_length=32,
        choices=GenericProductStatus.choices,
        default=GenericProductStatus.NEW,
    )

    objects = GeneriekProductQuerySet.as_manager()

    @property
    def upn_uri(self):
        return self.upn.upn_uri

    @property
    def upn_label(self):
        return self.upn.upn_label

    @property
    def is_sdg_product(self):
        return bool(self.upn.sdg)

    def generate_localized_information(
        self, language, **kwargs
    ) -> LocalizedGeneriekProduct:
        """Generate localized information for this generic product."""
        return LocalizedGeneriekProduct(
            generiek_product=self,
            taal=language,
            **kwargs,
        )

    class Meta:
        verbose_name = _("generiek product")
        verbose_name_plural = _("generieke producten")
        constraints = [
            models.UniqueConstraint(
                fields=["upn", "doelgroep"],
                name="unique_generic_product_upn_doelgroep",
            )
        ]

    def __str__(self):
        return f"{self.upn.upn_label}"


class Product(ProductFieldMixin, models.Model):
    """
    Product

    Container for localized products holding only the properties that are the
    same for every localized product.
    """

    class status(DjangoChoices):
        """The publication status of a product."""

        PUBLISHED = ChoiceItem("published", label=_("Gepubliceerd"))
        SCHEDULED = ChoiceItem("scheduled", label=_("Gepland"))
        CONCEPT = ChoiceItem("concept", label=_("Concept"))

    uuid = models.UUIDField(
        _("UUID"),
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_(
            "De identificatie die binnen deze API gebruikt wordt voor de resource."
        ),
    )
    generiek_product = models.ForeignKey(
        "producten.GeneriekProduct",
        related_name="producten",
        on_delete=models.PROTECT,
        verbose_name=_("generiek product"),
        help_text=_("Het generiek product gekoppeld aan dit product."),
    )
    referentie_product = models.ForeignKey(
        "self",
        related_name="specifieke_producten",
        on_delete=models.PROTECT,
        verbose_name=_("referentie product"),
        help_text=_(
            "Een referentie naar een product. "
            "Het toewijzen van een referentieproduct veronderstelt automatisch dat dit product specifiek is."
        ),
        blank=True,
        null=True,
    )
    catalogus = models.ForeignKey(
        "core.ProductenCatalogus",
        on_delete=models.CASCADE,
        related_name="producten",
        verbose_name=_("catalogus"),
        help_text=_("De catalogus waartoe dit product behoort."),
    )
    product_aanwezig = models.BooleanField(
        _("aanwezig"),
        help_text=_("Voert u dit product?"),
        blank=True,
        null=True,
    )
    product_valt_onder = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        verbose_name=_("product valt onder"),
        help_text=_("Een verwijzing naar een product waarvan dit product valt onder."),
        blank=True,
        null=True,
    )
    locaties = models.ManyToManyField(
        "organisaties.Lokatie",
        verbose_name=_("locaties"),
        related_name="producten",
        help_text=_(
            "De locaties die zijn toegewezen aan de product.",
        ),
        blank=True,
    )
    bevoegde_organisatie = models.ForeignKey(
        "organisaties.BevoegdeOrganisatie",
        on_delete=models.PROTECT,
        verbose_name=_("bevoegde organisatie"),
        related_name="producten",
        help_text=_("De bevoegde organisatie van de producten."),
    )

    heeft_kosten = models.BooleanField(
        _("heeft kosten"),
        help_text=_("Heeft dit product kosten?"),
        default=False,
    )
    api_verborgen = models.BooleanField(
        _("verborgen"),
        help_text=_("Verbergen voor Nationale Portalen."),
        default=False,
    )

    objects = ProductQuerySet.as_manager()

    @cached_property
    def upn(self):
        return self.generiek_product.upn

    @cached_property
    def is_referentie_product(self) -> bool:
        """:returns: Whether this is a reference product or not."""
        return bool(not self.referentie_product)

    @cached_property
    def has_expired(self) -> bool:
        """:returns: Whether this product has expired in relation to the reference product."""
        if self.is_referentie_product:
            return False
        if not self.most_recent_version:
            return False

        publication_date = self.most_recent_version.publicatie_datum
        reference_publication_date = self.most_recent_version.publicatie_datum

        return bool(
            (publication_date and reference_publication_date)
            and (publication_date < reference_publication_date)
        )

    @cached_property
    def beschikbare_talen(self) -> List[Language]:
        """
        :returns: A list of available languages for this product.
        """
        most_recent_version = self.most_recent_version
        if not most_recent_version:
            return []

        return [
            Language(
                name=t.get_taal_display(),
                code=t.taal,
                checked=getattr(t.generiek_informatie, "datum_check", None) is not None,
            )
            for t in most_recent_version.vertalingen.all()
        ]

    @cached_property
    def reference_product(self):
        """:returns: The reference product of this product."""
        return self if self.is_referentie_product else self.referentie_product

    @property
    def name(self):
        """:returns: The generic product's upn label."""
        return get_from_cache(
            self, "name", manager_methods=[ProductQuerySet.annotate_name]
        )

    @property
    def most_recent_version(self):
        """:returns: The most recent `ProductVersie`."""
        return get_from_cache(
            self, "most_recent_version", manager_methods=[ProductQuerySet.most_recent]
        )

    @property
    def active_version(self):
        """:returns: The most recent active `ProductVersie`."""
        return get_from_cache(
            self, "active_version", manager_methods=[ProductQuerySet.active]
        )

    def get_areas(self):
        """
        :returns: A list of areas matching the UPN's "sdg" codes.
        """
        from sdg.core.models import Thema

        return Thema.objects.filter(code__in=self.upn.sdg).values_list(
            "informatiegebied__informatiegebied", flat=True
        )

    def get_municipality_locations(self):
        """:returns: All available locations for this product. Selected locations are labeled as a boolean."""
        return self.catalogus.lokale_overheid.locaties.annotate(
            is_product_location=Case(
                When(
                    Q(pk__in=self.locaties.all().values_list("pk")),
                    then=Value(True),
                ),
                output_field=BooleanField(default=False),
            ),
        )

    def get_latest_versions(
        self, quantity=5, active=False, exclude_concept=False, reverse_order=True
    ):
        """:returns: The latest N versions for this product."""
        step_slice = 1 if reverse_order else 1
        queryset = self.versies.all().order_by("-versie")

        if active:
            queryset = queryset.filter(publicatie_datum__lte=datetime.date.today())
        if exclude_concept:
            queryset = queryset.exclude(publicatie_datum=None)

        return queryset[:quantity:step_slice]

    def get_all_versions(self, active=False, exclude_concept=False):
        """:returns: The versions for this product."""
        queryset = self.versies.all().order_by("-versie").select_related("gemaakt_door")

        if active:
            queryset = queryset.filter(publicatie_datum__lte=datetime.date.today())
        if exclude_concept:
            queryset = queryset.exclude(publicatie_datum=None)

        return queryset

    get_revision_list = partialmethod(get_latest_versions, reverse_order=False)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("producten")
        ordering = ["generiek_product__upn__upn_label"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "organisaties:catalogi:producten:edit",
            kwargs=build_url_kwargs(self),
        )

    def clean(self):
        from sdg.producten.models.validators import (
            validate_reference_product,
            validate_specific_product,
        )

        super().clean()

        if self.is_referentie_product:
            validate_reference_product(self)
        else:
            validate_specific_product(self)


class ProductVersie(ProductFieldMixin, models.Model):
    """
    Product Version

    The version of a product.
    """

    # TODO remove blank is true
    product = models.ForeignKey(
        "producten.Product",
        related_name="versies",
        on_delete=models.CASCADE,
        verbose_name=_("product"),
        help_text=_("Het product voor het product versie."),
        blank=True,
    )
    gemaakt_door = models.ForeignKey(
        User,
        related_name="productversies",
        on_delete=models.PROTECT,
        verbose_name=_("gemaakt door"),
        help_text=_("De maker van deze productversie."),
        blank=True,
        null=True,
    )
    versie = models.PositiveIntegerField(
        verbose_name=_("versie"),
        help_text=_("Het versienummer van het product."),
        default=1,
        blank=True,
    )

    publicatie_datum = models.DateField(
        _("publicatie datum"),
        help_text=_("De datum van publicatie van de productversie."),
        blank=True,
        null=True,
    )
    gemaakt_op = models.DateTimeField(
        _("gemaakt op"),
        help_text=_("De oorspronkelijke aanmaakdatum voor deze productversie."),
        auto_now_add=True,
    )
    gewijzigd_op = models.DateTimeField(
        _("gewijzigd op"),
        help_text=_("De wijzigingsdatum voor deze productversie."),
        auto_now=True,
    )

    bewerkte_velden = JSONField(
        verbose_name=_("bewerkte_velden"),
        blank=True,
        default=dict,
    )
    interne_opmerkingen = models.TextField(
        _("interne opmerkingen"),
        help_text=_(
            "Interne opmerkingen die niet zichtbaar zijn buiten deze omgeving."
        ),
        blank=True,
    )

    objects = ProductVersieQuerySet.as_manager()

    @property
    def current_status(self) -> Any[Product.status]:
        """:returns: The current publishing status for this product version."""
        if not self.publicatie_datum:
            return Product.status.CONCEPT
        elif self.publicatie_datum <= datetime.date.today():
            return Product.status.PUBLISHED
        else:
            return Product.status.SCHEDULED

    @property
    def as_html(self):
        return render_to_string(
            "producten/_include/productversie.html",
            context={"version": self},
        )

    def generate_localized_information(self, language, **kwargs) -> LocalizedProduct:
        """Generate localized information for this product."""
        return LocalizedProduct(
            product_versie=self,
            taal=language,
            **kwargs,
        )

    def update_with_reference_texts(
        self,
        reference_product_version,
        languages: Optional[List[TaalChoices]] = None,
        skip_filled_fields=False,
    ):
        language_version_map = {
            rpv.taal: rpv for rpv in reference_product_version.vertalingen.all()
        }
        if languages:
            language_version_map = {
                k: v for k, v in language_version_map.items() if k in languages
            }

        for localized_product_version in self.vertalingen.all():
            if localized_reference_product_version := language_version_map.get(
                localized_product_version.taal, None
            ):
                localized_product_version.update_with_reference_texts(
                    localized_reference_product_version,
                    skip_filled_fields=skip_filled_fields,
                )

    def get_pretty_version(self):
        concept = "(concept)" if not self.publicatie_datum else ""
        return f"{self.versie} {concept}".strip()

    def get_pretty_name(self):
        try:
            return f"{self.product} — versie {self.get_pretty_version()}"
        except self._meta.model.product.RelatedObjectDoesNotExist:
            return f"Unknown product - versie {self.get_pretty_version()}"

    class Meta:
        verbose_name = _("product versie")
        verbose_name_plural = _("product versies")
        ordering = ("-versie",)

    def __str__(self):
        return self.get_pretty_name()

    def clean(self):
        super().clean()

        if not self.pk:
            # Validators for new instances
            if self.publicatie_datum and is_past_date(self.publicatie_datum):
                raise ValidationError(
                    _("De publicatiedatum kan niet in het verleden liggen.")
                )


class Productuitvoering(models.Model):
    """
    Product variant

    Container for localized product variants holding only the properties that
    are the same for every localized product variant.
    """

    product = models.ForeignKey(
        "producten.Product",
        related_name="uitvoeringen",
        on_delete=models.PROTECT,
        verbose_name=_("product"),
        help_text=_("Het product voor het productuitvoering."),
    )

    class Meta:
        verbose_name = _("productuitvoering")
        verbose_name_plural = _("productuitvoeringen")

    def __str__(self):
        return f"{self.product} (uitvoering)"
