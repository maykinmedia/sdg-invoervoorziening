from itertools import chain

from django import forms


class DynamicArrayWidget(forms.TextInput):

    template_name = "forms/widgets/dynamic_array.html"

    def __init__(self, *args, **kwargs):
        self.subwidget_form = kwargs.pop("subwidget_form", forms.TextInput)
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context_value = value or [""]
        context = super().get_context(name, context_value, attrs)

        final_attrs = context["widget"]["attrs"]
        id_ = context["widget"]["attrs"].get("id")
        context["widget"]["is_none"] = value is None

        if getattr(self.subwidget_form, "chunk", False):
            context["widget"]["value"] = self.subwidget_form.chunk(
                context["widget"]["value"], 2
            )

        subwidgets = []
        for index, item in enumerate(context["widget"]["value"]):
            widget_attrs = final_attrs.copy()
            if id_:
                widget_attrs["id"] = "{id_}_{index}".format(id_=id_, index=index)
            widget = self.subwidget_form()
            context["widget"]["single"] = getattr(widget, "single", False)
            widget.is_required = self.is_required
            subwidgets.append(widget.get_context(name, item, widget_attrs)["widget"])

        context["widget"]["subwidgets"] = subwidgets
        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
            return [value for value in getter(name) if value]
        except AttributeError:
            return data.get(name)

    def value_omitted_from_data(self, data, files, name):
        return False

    def format_value(self, value):
        return value or []


class LabeledWidget(forms.TextInput):
    template_name = None

    @staticmethod
    def chunk(input_list, chunk_size: int):
        """Flatten and divide an iterable into even sized chunks."""
        if isinstance(input_list[0], list):
            input_list = list(chain.from_iterable(input_list))

        input_list = [
            input_list[i:i + chunk_size]
            for i in range(0, len(input_list), chunk_size)  # fmt: skip
        ]
        return input_list

    def get_context(self, name, value, attrs):
        context_value = ["", ""]

        if isinstance(value, list) and len(value) == 2:
            context_value = value
        context = super().get_context(name, context_value, attrs)
        context["widget"]["label_value"] = context_value[0]
        context["widget"]["field_value"] = context_value[1]

        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
            return [value for value in getter(name) if value]
        except AttributeError:
            return data.get(name)

    def value_omitted_from_data(self, data, files, name):
        return False

    def format_value(self, value):
        return value or []


class LabeledURLWidget(LabeledWidget):
    template_name = "forms/widgets/labeled_url_field.html"


class LabeledTooltipWidget(LabeledWidget):
    template_name = "forms/widgets/labeled_tooltip_field.html"
    single = True
