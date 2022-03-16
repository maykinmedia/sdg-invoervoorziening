from django import forms
from django.forms import inlineformset_factory

from sdg.core.forms import DynamicArrayField
from sdg.organisaties.constants import opening_times_error_messages
from sdg.organisaties.models import LokaleOverheid, Lokatie as Locatie


class LokaleOverheidForm(forms.ModelForm):
    class Meta:
        model = LokaleOverheid
        fields = (
            "organisatie",
            "contact_naam",
            "contact_website",
            "contact_telefoonnummer",
            "contact_emailadres",
        )

    readonly_fields = ("organisatie",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in self.readonly_fields:
                field.widget.attrs["readonly"] = True
            if field.label.startswith("Contact"):
                field.label = field.label.replace("Contact ", "").title()

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data = {
            k: v for k, v in cleaned_data.items() if k not in self.readonly_fields
        }
        return cleaned_data


class LocatieForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, DynamicArrayField):
                field.error_messages.update(opening_times_error_messages)

    class Meta:
        model = Locatie
        fields = (
            "naam",
            "straat",
            "nummer",
            "postcode",
            "plaats",
            "land",
            "maandag",
            "dinsdag",
            "woensdag",
            "donderdag",
            "vrijdag",
            "zaterdag",
            "zondag",
            "openingstijden_opmerking",
        )


LocatieInlineFormSet = inlineformset_factory(
    LokaleOverheid, Locatie, form=LocatieForm, extra=0
)
