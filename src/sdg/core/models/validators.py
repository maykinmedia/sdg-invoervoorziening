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


def validate_uppercase(value):
    return uppercase_validator(value)


def validate_lau(value):
    return lau_validator(value)
