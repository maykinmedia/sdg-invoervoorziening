from copy import deepcopy

from django.db import models
from django.db.models import BooleanField, Case, Q, Value, When
from django.utils.timezone import now


class ProductenCatalogusQuerySet(models.QuerySet):
    ...

    def specific_catalogs(self, municipality):
        """
        Get specific catalogs for the given municipality.
        Select the reference catalog for extra performance.
        Annotate whether the reference catalog is owned by the municipality.
        """
        return (
            self.filter(
                lokale_overheid=municipality,
                is_referentie_catalogus=False,
            )
            .select_related(
                "referentie_catalogus",
            )
            .annotate(
                municipality_owns_reference=Case(
                    When(
                        referentie_catalogus__lokale_overheid=municipality,
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        )

    def annotate_area_and_products(self):
        """
        Annotate all area and products to specific catalogs.
        """
        from sdg.core.models import Thema

        themes = (
            Thema.objects.all()
            .select_related("informatiegebied")
            .prefetch_related("upn")
        )
        area_and_products = {
            theme.informatiegebied.informatiegebied: set() for theme in themes
        }
        for catalog in self:
            setattr(catalog, "area_and_products", deepcopy(area_and_products))
            if catalog.municipality_owns_reference:
                ref_catalog = catalog.referentie_catalogus
                setattr(ref_catalog, "area_and_products", deepcopy(area_and_products))
        return self


class OrganisatieManager(models.Manager):
    def active(self):
        return self.filter(Q(owms_end_date__lte=now()))
