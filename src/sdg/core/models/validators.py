from django.core.validators import _lazy_re_compile, RegexValidator
from django.utils.translation import ugettext_lazy as _

uppercase_validator = RegexValidator(
    _lazy_re_compile("^[A-Z]*$"),
    message=_("Voer alleen hoofdletters in."),
    code="invalid",
)


def validate_uppercase(value):
    return uppercase_validator(value)
