from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from sdg.producten.models import Product


def validate_specific_product(product: Product):
    if product.catalogus.is_referentie_catalogus:
        raise ValidationError(
            _("Dit specifieke product moet in een specifieke catalogus staan.")
        )
    if product.generiek_product:
        raise ValidationError(
            _(
                'Het veld "generiek_product" kan alleen worden toegevoegd als dit product een referentieproduct is.'
            )
        )
    if not product.referentie_product.catalogus.is_referentie_catalogus:
        raise ValidationError(
            _(
                "Het referentieproduct van dit product moet in een referentiecatalogus staan."
            )
        )


def validate_reference_product(product: Product):
    if not product.catalogus.is_referentie_catalogus:
        raise ValidationError(
            _("Dit referentieproduct moet in een referentiecatalogus staan.")
        )
    if not product.generiek_product:
        raise ValidationError(
            _("Een referentieproduct moet een generiek product hebben.")
        )
