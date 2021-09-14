import re

from django.core.validators import RegexValidator, _lazy_re_compile
from django.utils.translation import ugettext_lazy as _

uppercase_validator = RegexValidator(
    _lazy_re_compile(r"^[A-Z]*$"),
    message=_("Voer alleen hoofdletters in."),
    code="invalid",
)

lau_validator = RegexValidator(
    _lazy_re_compile(r"^NL\d{1,3}$"),
    message=_("Voer een geldige LAU code in."),
    code="invalid",
)

postcode_validator = RegexValidator(
    _lazy_re_compile(r"^[1-9][0-9]{3} ?(?!sa|sd|ss)[a-z]{2}$", re.IGNORECASE),
    message=_("Voer een geldige LAU code in."),
    code="invalid",
)

openingstijden_validator = RegexValidator(
    _lazy_re_compile(r"^[0-9]{1,2}(:|\.)[0-9]{2}(\s?-\s?[0-9]{1,2}(:|\.)[0-9]{2})?$"),
    message=_("Voer een geldige openingstijd in."),
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
