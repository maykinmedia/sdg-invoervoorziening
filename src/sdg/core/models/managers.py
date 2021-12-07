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

    def create_specific_catalogs(self, municipality):
        """Create a specific catalog (if it doesn't exist) for each reference catalog."""
        catalog_list = [
            self.model(
                referentie_catalogus=catalog,
                lokale_overheid=municipality,
                is_referentie_catalogus=False,
                domein=catalog.domein,
                versie=catalog.versie,
                naam=f"{municipality} ({catalog.naam})",
            )
            for catalog in self.model.objects.filter(
                is_referentie_catalogus=True,
                automatisch_catalogus_aanmaken=True,
            )
        ]
        self.bulk_create(catalog_list, ignore_conflicts=True)


class OrganisatieQuerySet(models.QuerySet):
    def active(self):
        return self.filter(owms_end_date__lte=now())
