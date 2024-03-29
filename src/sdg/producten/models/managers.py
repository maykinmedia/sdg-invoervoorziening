from datetime import date

from django.conf import settings
from django.db import models
from django.db.models import Exists, F, Max, OuterRef, Prefetch, Q, Subquery
from django.utils.timezone import now

from sdg.core.constants import GenericProductStatus


class ProductQuerySet(models.QuerySet):
    def active(self, active_on=None, exclude_inactive_products=False):
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
            .filter(product=OuterRef("product"))
            .order_by("-versie")
            .values_list("pk", flat=True)[:1]
        )

        queryset = self

        # First, filter out products that do not have active versions at
        # all, if so needed.
        if exclude_inactive_products:
            queryset = self.filter(
                Exists(
                    ProductVersie.objects.exclude(publicatie_datum=None).filter(
                        publicatie_datum__lte=active_on, product=OuterRef("pk")
                    )
                )
            )

        # Second, make sure we prefetch the correct active version for
        # performance.
        return queryset.prefetch_related(
            Prefetch(
                "versies",
                to_attr="_active_version",
                queryset=ProductVersie.objects.filter(pk__in=subquery).prefetch_related(
                    "vertalingen"
                ),
            )
        )

    def active_organization(self):
        """
        Filter the products to only include products from active organizations.
        """
        return self.filter(
            Q(catalogus__lokale_overheid__organisatie__owms_end_date__gte=now())
            | Q(catalogus__lokale_overheid__organisatie__owms_end_date__isnull=True)
        )

    def most_recent(self):
        """
        The most recent product is the product that was last published
        (including future publications) or a concept.

        This function optimizes the queryset to prefetch the most recent
        `ProductVersie`, including the appropriate prefetched translations. The
        prefetched most recent version is available via
        `Product._most_recent_version` and is always a list, containing 0 or 1
        `ProductVersie`.
        """
        from sdg.producten.models import ProductVersie

        subquery = Subquery(
            ProductVersie.objects.filter(product=OuterRef("product"))
            .order_by("-versie")
            .values_list("pk", flat=True)[:1]
        )

        return self.prefetch_related(
            Prefetch(
                "versies",
                to_attr="_most_recent_version",
                queryset=ProductVersie.objects.filter(pk__in=subquery).prefetch_related(
                    "vertalingen",
                    "product__generiek_product__vertalingen",
                ),
            )
        )

    def annotate_name(self):
        """
        Annotate the name for the product.
        The field is filled with the data from the specific or reference product depending on
        whether `referentie_product` exists.
        """
        return self.annotate(
            _name=F("generiek_product__upn__upn_label"),
        )

    def annotate_latest_publication_date(self):
        return self.annotate(_latest_publication_date=Max("versies__publicatie_datum"))

    def select_generic(self):
        """
        Select additional generic product data for extra performance.
        """
        return self.select_related(
            "generiek_product",
            "generiek_product__upn",
            "referentie_product",
        )

    def exclude_generic_status(self, api=False):
        """
        Exclude products with certain generic product status.
        """
        if not api:
            return self.exclude(
                Q(
                    catalogus__is_referentie_catalogus=False,
                    generiek_product__product_status__in=GenericProductStatus.get_cms_excluded(),
                )
                | Q(
                    catalogus__is_referentie_catalogus=True,
                    generiek_product__product_status__in=GenericProductStatus.get_cms_excluded(
                        reference=True
                    ),
                ),
            )
        else:
            return self.exclude(
                generiek_product__product_status__in=GenericProductStatus.get_api_excluded(),
            )


class GeneriekProductQuerySet(models.QuerySet):
    def exclude_generic_status(self, api=False):
        """
        Exclude generic products with certain product status.
        """
        if not api:
            return self
        else:
            return self.exclude(
                product_status__in=GenericProductStatus.get_api_excluded(),
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

    # FIXME: Remove?
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


class LocalizedGeneriekProductManager(LocalizedManager):
    def sdg(self, org_type=None):
        from sdg.core.models import UniformeProductnaam

        if org_type is None:
            mapping = {
                "municipality": "gemeente",
                "province": "provincie",
                "waterauthority": "waterschap",
            }
            org_type = mapping[settings.SDG_ORGANIZATION_TYPE]

        if org_type in UniformeProductnaam.ORGANIZATION_FIELDS:
            return self.filter(
                **{
                    "generiek_product__upn__sdg__len__gt": 0,
                    "generiek_product__upn__{}".format(org_type): True,
                }
            )

        raise ValueError(
            "Parameter 'org_type' is '{}' but it must be in {}".format(
                org_type, ", ".join(UniformeProductnaam.ORGANIZATION_FIELDS)
            )
        )
