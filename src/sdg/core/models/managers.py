from django.db import models
from django.db.models import BooleanField, Case, F, Value, When
from django.utils.timezone import now


class ProductenCatalogusQuerySet(models.QuerySet):
    def specific_catalogs(self):
        """
        Get specific catalogs for the given municipality.
        Select the reference catalog for extra performance.
        Annotate whether the reference catalog is owned by the municipality.
        """
        return (
            self.filter(
                is_referentie_catalogus=False,
            )
            .select_related(
                "referentie_catalogus",
            )
            .annotate(
                municipality_owns_reference=Case(
                    When(
                        referentie_catalogus__lokale_overheid=F("lokale_overheid"),
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        )


class OrganisatieQuerySet(models.QuerySet):
    def active(self):
        return self.filter(owms_end_date__lte=now())
