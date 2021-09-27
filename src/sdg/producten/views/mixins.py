from django.forms import BaseFormSet


def make_form_optional(form_class):
    """Make all the fields of a form/formset optional."""

    def _process_form(form):
        for name, field in form.fields.items():
            field.required = False

    if isinstance(form_class, BaseFormSet):
        # process formset
        for form in form_class.forms:
            _process_form(form)
    else:
        _process_form(form_class)

    return form_class
