import re
from functools import partial

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator, _lazy_re_compile
from django.utils.translation import gettext_lazy as _


class DomainValidator(URLValidator):
    def __call__(self, value):
        return super().__call__(f"https://{value}")


uppercase_validator = RegexValidator(
    _lazy_re_compile(r"^[A-Z]*$"),
    message=_("Voer alleen hoofdletters in."),
    code="invalid",
)

lau_validator = RegexValidator(
    _lazy_re_compile(r"^NL\d{1,3}$"),
    message=_("Voer een geldige LAU code in. Bijvoorbeeld: NL123"),
    code="invalid",
)

postcode_validator = RegexValidator(
    _lazy_re_compile(r"^[1-9][0-9]{3} ?(?!sa|sd|ss)[a-z]{2}$", re.IGNORECASE),
    message=_("Voer een geldige postcode code in. Bijvoorbeeld: 1234AA"),
    code="invalid",
)

openingstijden_validator = RegexValidator(
    _lazy_re_compile(r"^(\s?[0-9]{1,2}[:.][0-9]{2}(?:\s?-\s?[0-9]{1,2}[:.][0-9]{2}))$"),
    message=_(
        "Voer een geldige openingstijd in of laat leeg indien gesloten. Bijvoorbeeld: 09:00 - 17:00"
    ),
    code="invalid",
)

url_validator = URLValidator(
    message=_("Voer een geldige URL in."),
    code="invalid",
)


def validate_uppercase(value):
    return uppercase_validator(value)


def validate_lau(value):
    return lau_validator(value)


def validate_postcode(value):
    return postcode_validator(value)


def validate_openingstijden(value):
    return openingstijden_validator(value)


def validate_labeled_url(array, length=2):
    """Ensure the array length equals two and the second item is a valid URL."""
    for sub_array in array:
        if len(sub_array) != length:
            raise ValidationError(
                _("De link moet een label en een URL bevatten."), code="invalid"
            )

        url_validator(sub_array[1])


validate_labeled_url_with_category = partial(validate_labeled_url, length=3)


def validate_reference_catalog(catalog):
    if catalog.has_reference_catalog():
        raise ValidationError(
            _('Een referentiecatalogus kan geen "referentie_catalogus" hebben.')
        )


def validate_specific_catalog(catalog):
    if not catalog.has_reference_catalog():
        raise ValidationError(_("Een catalogus moet een referentiecatalogus hebben."))
    if not catalog.referentie_catalogus.is_referentie_catalogus:
        raise ValidationError(
            _(
                'Een catalogus kan alleen naar een catalogus linken als "is_referentie_catalogus" is ingeschakeld.'
            )
        )
