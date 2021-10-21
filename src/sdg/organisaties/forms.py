from django import forms
from django.forms import inlineformset_factory

from sdg.organisaties.models import LokaleOverheid, Lokatie


class LokaleOverheidForm(forms.ModelForm):
    class Meta:
        model = LokaleOverheid
        fields = (
            "ondersteunings_organisatie",
            "verantwoordelijke_organisatie",
            "bevoegde_organisatie",
            "organisatie",
            "contact_naam",
            "contact_website",
            "contact_telefoonnummer",
            "contact_emailadres",
        )


class LokatieForm(forms.ModelForm):
    class Meta:
        model = Lokatie
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
        )


LokatieInlineFormSet = inlineformset_factory(
    LokaleOverheid, Lokatie, form=LokatieForm, extra=0
)
