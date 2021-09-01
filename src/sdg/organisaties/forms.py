from django import forms
from django.urls import reverse
from django.utils.translation import gettext as _

from sdg.core.forms.mixins import SdgFormMixin
from sdg.organisaties.models import LokaleOverheid


class LokaleOverheidForm(SdgFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_action = reverse(
            "organisaties:overheid_edit",
            kwargs={
                "pk": self.instance.pk,
            },
        )
        self._append_html(
            """
        <div class="form__add-subform">
            <i class="fas fa-plus"></i>
            Nog een locatie toevoegen
        </div>
        """
        )
        self._insert_input_button("Opslaan", _("Opslaan"))

    class Meta:
        model = LokaleOverheid
        fields = (
            "ondersteunings_organisatie",
            "verantwoordelijke_organisatie",
            "bevoegde_organisatie",
            "organisatie",
            "lau_code",
            "contact_naam",
            "contact_website",
            "contact_telefoonnummer",
            "contact_emailadres",
        )
