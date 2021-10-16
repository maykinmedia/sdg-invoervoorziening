from django.forms.widgets import ChoiceWidget


class ProductRadioSelect(ChoiceWidget):
    input_type = "radio"
    template_name = "forms/widgets/radio.html"
    option_template_name = "forms/widgets/radio_option.html"
