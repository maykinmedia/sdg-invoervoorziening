from html.parser import HTMLParser

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, _lazy_re_compile
from django.utils.translation import gettext_lazy as _

import markdown

SIMPLE_HTML_REGEX = _lazy_re_compile(
    r"""<[A-Za-z\s="']+?>.*?<\/[A-Za-z\s="']+?>|<[A-Za-z\s="']+?\/>"""
)
HTML_TAGS_TO_TEXT = {
    "h1": "Kop 1",
    "h2": "Kop 2",
    "h5": "Kop 5",
    "h6": "Kop 6",
    "hr": "Horizontale lijn",
    "img": "Afbeelding",
    "code": "Code",
}


class AllowedMarkdownValidator(HTMLParser):
    prohibited_html_tags = ["h1", "h2", "h5", "h6", "hr", "img", "code"]

    def handle_starttag(self, tag, attr):
        if tag in self.prohibited_html_tags:
            self.data = tag


no_html_validator = RegexValidator(
    SIMPLE_HTML_REGEX,
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

    parser = AllowedMarkdownValidator()
    parser.feed(html_text)

    if hasattr(parser, "data"):
        raise ValidationError(
            _("Het veld mag geen '{html_element}' in Markdown bevatten.").format(
                html_element=str(HTML_TAGS_TO_TEXT[parser.data])
            )
        )


def validate_https(value):
    if not value.startswith("https"):
        raise ValidationError(
            _("De URL moet beginnen met 'https://'. Let op de 's' achter 'http'.")
        )


def validate_product(localized):
    """Validate a product (specific / reference).
    - If `product_aanwezig` is False, the product must declare `product_aanwezig_toelichting`.
    """

    if (
        localized.product_versie.product.product_aanwezig is False
        and not localized.product_aanwezig_toelichting
    ):
        raise ValidationError({
            "product_aanwezig_toelichting": _(
                "Het veld 'Product aanwezig toelichting' is verplicht als product niet aanwezig is."
            )
        })

    if bool(localized.decentrale_procedure_label) is not bool(
        localized.decentrale_procedure_link
    ):
        raise ValidationError(
            {
                "decentrale_procedure_link": _(
                    "De link moet een label en een URL bevatten.",
                )
            }
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
