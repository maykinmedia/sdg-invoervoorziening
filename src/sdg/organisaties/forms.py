from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from sdg.core.forms import DynamicArrayField
from sdg.organisaties.constants import opening_times_error_messages
from sdg.organisaties.models import (
    BevoegdeOrganisatie,
    LokaleOverheid,
    Lokatie as Locatie,
)


class LokaleOverheidForm(forms.ModelForm):
    class Meta:
        model = LokaleOverheid
        fields = (
            "organisatie",
            "contact_website",
            "contact_telefoonnummer",
            "contact_emailadres",
            "contact_formulier_link",
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


class BevoegdeOrganisatieForm(forms.ModelForm):

    staat_niet_in_de_lijst = forms.BooleanField(
        label=_("Mijn bevoegde organisatie staat niet in de lijst."),
        required=False,
    )

    class Meta:
        model = BevoegdeOrganisatie
        fields = (
            "naam",
            "organisatie",
            "staat_niet_in_de_lijst",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["naam"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data["naam"] and cleaned_data["organisatie"]:
            cleaned_data["naam"] = cleaned_data["organisatie"].owms_pref_label
        return cleaned_data


BevoegdeOrganisatieInlineFormSet = inlineformset_factory(
    LokaleOverheid, BevoegdeOrganisatie, form=BevoegdeOrganisatieForm, extra=0
)
