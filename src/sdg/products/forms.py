from django import forms

from markdownx.fields import MarkdownxFormField


# TODO: Implement markdown editor
class ProductEditForm(forms.Form):
    description = MarkdownxFormField()
    procedure = MarkdownxFormField()
    exceptions = MarkdownxFormField()
