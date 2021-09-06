from django import forms


# TODO: Implement markdown editor
class ProductEditForm(forms.Form):
    description = forms.CharField()
    procedure = forms.CharField()
    exceptions = forms.CharField()
