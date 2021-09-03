from django import forms

from ckeditor.widgets import CKEditorWidget


class ProductEditForm(forms.Form):
    description = forms.CharField(widget=CKEditorWidget())
    procedure = forms.CharField(widget=CKEditorWidget())
    exceptions = forms.CharField(widget=CKEditorWidget())
