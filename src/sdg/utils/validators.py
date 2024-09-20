import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _


def validate_charfield_entry(value, allow_apostrophe=False):
    """
    Validates a charfield entry according with Belastingdienst requirements.

    :param value: The input value string to be validated.
    :param allow_apostrophe: Boolean to add the apostrophe character to the
    validation. Apostrophes are allowed in input with ``True`` value. Defaults
    to ``False``.
    :return: The input value if validation passed. Otherwise, raises a
    ``ValidationError`` exception.
    """
    invalid_chars = '/"\\,;' if allow_apostrophe else "/\"\\,;'"

    for char in invalid_chars:
        if char in value:
            raise ValidationError(_("Uw invoer bevat een ongeldig teken: %s") % char)
    return value


def validate_phone_number(value):
    try:
        int(value.strip().lstrip("0+").replace("-", "").replace(" ", ""))
    except (ValueError, TypeError):
        raise ValidationError(_("Het opgegeven mobiele telefoonnummer is ongeldig."))

    return value


class CustomRegexValidator(RegexValidator):
    """
    CustomRegexValidator because the validated value is append to the message.
    """

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        if not self.regex.search(force_str(value)):
            message = "{0}: {1}".format(self.message, force_str(value))
            raise ValidationError(message, code=self.code)


validate_postal_code = CustomRegexValidator(
    regex="^[1-9][0-9]{3} ?[a-zA-Z]{2}$", message=_("Ongeldige postcode")
)


def validate_placeholders(value, form=None, field_name=None):
    """
    Ensure the form value does not contain any placeholders.

    i.e. [placeholder] or XXX
    """
    placeholder_re = re.compile(r"\[.*?](?!\()|[Xx]{2,}")

    if (form and not field_name) or (not form and field_name):
        raise ValueError("Both form and field_name or neither must be provided")

    if not isinstance(value, str):
        return

    if placeholder_re.search(value):
        if not form:
            return True

        form.add_error(
            field_name,
            'De Nederlandse en Engelse teksten mogen geen placeholders zoals "[" , "]" of "XX" bevatten. Graag deze tekens in beide talen verwijderen in de teksten en opnieuw opslaan.',
        )
