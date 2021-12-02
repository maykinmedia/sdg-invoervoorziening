from datetime import date

from django.db import models
from django.db.models import Case, F, Prefetch, Subquery, When


class ProductQuerySet(models.QuerySet):
    def active(self, active_on=None):
        """
        An active product is a product with its product version and its
        translations as it was most recently published.

        Unpublished (future versions or concept versions) products are not
        included.

        This function optimizes the queryset to prefetch the `ProductVersie`
        that is active on given `active_on` date, including the appropriate
        prefetched translations. The prefetched active version is available
        via `Product.active_version` and is always a list, containing 0 or 1
        `ProductVersie`.
        """
        from sdg.producten.models import ProductVersie

        if active_on is None:
            active_on = date.today()

        subquery = Subquery(
            ProductVersie.objects.exclude(publicatie_datum=None)
            .filter(publicatie_datum__lte=active_on)
            .order_by("-versie")
            .values_list("pk", flat=True)[:1]
        )

        return self.prefetch_related(
            Prefetch(
                "versies",
                to_attr="active_versions",
                queryset=ProductVersie.objects.filter(pk__in=subquery).prefetch_related(
                    "vertalingen"
                ),
            )
        )

    def most_recent(self):
        """
        The most recent product is the product that was last published
        (including future publications) or a concept.

        This function optimizes the queryset to prefetch the most recent
        `ProductVersie`, including the appropriate prefetched translations. The
        prefetched most recent version is available via
        `Product.most_recent_version` and is always a list, containing 0 or 1
        `ProductVersie`.
        """
        from sdg.producten.models import ProductVersie

        subquery = Subquery(
            ProductVersie.objects.order_by("-versie").values_list("pk", flat=True)[:1]
        )

        return self.prefetch_related(
            Prefetch(
                "versies",
                to_attr="most_recent_version",
                queryset=ProductVersie.objects.filter(pk__in=subquery).prefetch_related(
                    "vertalingen"
                ),
            )
        )

    def annotate_is_reference(self):
        """
        Annotate whether this product is a reference product.
        """
        return self.annotate(
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


class ProductVersieQuerySet(models.QuerySet):
    def published(self):
        """
        Returns versions that are published (ie. not concepts).
        """
        return self.exclude(publicatie_datum=None)


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
