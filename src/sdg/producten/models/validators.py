from html.parser import HTMLParser

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, _lazy_re_compile
from django.utils.translation import gettext_lazy as _

import markdown

prohibited_html_tags = ["h1", "h2", "h5", "h6", "hr", "img", "code"]


class allowedMarkdownValidator(HTMLParser):
    def handle_starttag(self, tag, attr):
        if tag in prohibited_html_tags:
            self.data = tag


no_html_validator = RegexValidator(
    _lazy_re_compile(r"<(.*)>.*?|<(.*) \>"),
    message=_(
        "Het veld mag geen HTML-tags bevatten. Zorg ervoor dat de tabel een header rij heeft."
    ),
    code="invalid",
    inverse_match=True,
)


def validate_no_html(value):
    return no_html_validator(value)


def validate_markdown(value):
    """Valiates a markdown field to check if it doesn't have any unwanted html characters:
    - `h1`, `h2`, `h5`, `h6`, `hr`, `img`, `code`
    """

    html_text = markdown.markdown(value)

    parser = allowedMarkdownValidator()
    parser.feed(html_text)

    if hasattr(parser, "data"):
        raise ValidationError(
            _("Het veld mag geen instantie van <{html_element}> bevatten.").format(
                html_element=str(parser.data)
            )
        )


def validate_product(localized):
    """Validate a product (specific / reference).
    - If `product_aanwezig` is False, the product must declare `product_aanwezig_toelichting`.
    """

    if (
        localized.product_versie.product.product_aanwezig is False
        and not localized.product_aanwezig_toelichting
    ):
        raise ValidationError(
            _(
                "Het veld 'product_aanwezig_toelichting' is verplicht als het veld 'product_aanwezig' is uitgeschakeld."
            )
        )


def validate_specific_product(product):
    """Validate a specific product.
    - The product must have a reference product.
    - The product's catalog cannot be a referentie catalogus
    - The product cannot have a generic product.
    """

    if product.catalogus.is_referentie_catalogus:
        raise ValidationError(
            _("Dit specifieke product moet in een specifieke catalogus staan.")
        )
    if product.generiek_product != product.referentie_product.generiek_product:
        raise ValidationError(
            _(
                "Het veld generieke product moet gelijk zijn aan het generieke product van het referentieproduct."
            )
        )
    if not product.referentie_product.catalogus.is_referentie_catalogus:
        raise ValidationError(
            _(
                "Het referentieproduct van dit product moet in een referentiecatalogus staan."
            )
        )


def validate_reference_product(product):
    """Validate a reference product.
    - The product's catalog must be a referentie catalogus.
    - The product must have a generic product.
    """

    if not product.catalogus.is_referentie_catalogus:
        raise ValidationError(
            _("Dit referentieproduct moet in een referentiecatalogus staan.")
        )
