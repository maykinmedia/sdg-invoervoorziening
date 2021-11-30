from django.db import models
from django.db.models import Case, Exists, ExpressionWrapper, F, When


class ProductQuerySet(models.QuerySet):
    def annotate_is_reference(self):
        """
        Annotate whether this product is a reference product.
        """
        self.annotate(
            has_referentie_product=models.Case(
                models.When(referentie_product__isnull=True, then=models.Value(True)),
                default=models.Value(False),
                output_field=models.BooleanField(),
            )
        )

    def annotate_name_and_area(self):
        """
        Annotate `name` and `area` fields.
        The name and area fields are filled with the data from the specific or reference product depending on
        whether referentie_product exists.
        """
        return self.annotate(
            name=Case(
                When(
                    referentie_product__isnull=False,
                    then=F("referentie_product__generiek_product__upn__upn_label"),
                ),
                default=F("generiek_product__upn__upn_label"),
            ),
            area=Case(
                When(
                    referentie_product__isnull=False,
                    then=F(
                        "referentie_product__generiek_product__upn__thema__informatiegebied__informatiegebied"
                    ),
                ),
                default=F(
                    "generiek_product__upn__thema__informatiegebied__informatiegebied"
                ),
            ),
        )

    def select_generic(self):
        """
        Select additional generic product data for extra performance.
        """
        return self.select_related(
            "generiek_product",
            "generiek_product__upn",
            "referentie_product",
            "referentie_product__generiek_product",
            "referentie_product__generiek_product__upn",
        )


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)


class LocalizedManager(models.Manager):
    def localize(self, instance, languages, **kwargs):
        """Localize product instance with the given languages."""
        return self.bulk_create(
            [
                instance.generate_localized_information(language=language, **kwargs)
                for language in languages
            ],
            ignore_conflicts=True,
        )

    def bulk_localize(self, instances, languages, **kwargs):
        """Bulk-localize product instances with the given languages."""
        create_list = []
        for instance in instances:  # avoid double list comprehension for readability
            create_list.extend(
                [
                    instance.generate_localized_information(language=language, **kwargs)
                    for language in languages
                ],
            )
        return self.bulk_create(create_list, ignore_conflicts=True)
