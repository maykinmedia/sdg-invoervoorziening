from markdownx.models import MarkdownxField as _MarkdownxField

from sdg.producten.models.validators import validate_no_html


class MarkdownxField(_MarkdownxField):
    """Override `MarkdownxField` with custom validators."""

    validators = [validate_no_html]
