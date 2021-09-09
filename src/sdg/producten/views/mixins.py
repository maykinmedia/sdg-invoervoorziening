class OptionalFormMixin:
    def get_form(self, *args, **kwargs):
        form_class = super().get_form(*args, **kwargs)
        for name, field in form_class.fields.items():
            field.required = False
        return form_class


class StandaardMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["standaard"] = True
        return context
