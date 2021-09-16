from django.forms import BaseFormSet, inlineformset_factory

from sdg.producten.forms import GegevensFormHelper, ProductGegevensForm


class OptionalFormMixin:
    @staticmethod
    def _process_form(form):
        for name, field in form.fields.items():
            field.required = False

    def get_form(self, *args, **kwargs):
        form_class = super().get_form(*args, **kwargs)

        if isinstance(form_class, BaseFormSet):
            # process formset
            for form in form_class.forms:
                self._process_form(form)
        else:
            self._process_form(form_class)

        return form_class


class ProductFormSetMixin:
    context_object_name = "product"
    parent_model = None
    child_model = None

    def __init__(self, *args, **kwargs):
        self.model = self.parent_model
        self.form_class = inlineformset_factory(
            self.parent_model,
            self.child_model,
            form=ProductGegevensForm,
        )
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_helper"] = GegevensFormHelper()
        return context
