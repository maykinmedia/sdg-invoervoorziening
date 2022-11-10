from django.conf import settings
from django.views.generic.base import ContextMixin


class SDGSettingsMixin(ContextMixin):
    """
    Add SDG related settings to the context.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            SDG_CMS_PRODUCTS_DISABLED=getattr(
                settings, "SDG_CMS_PRODUCTS_DISABLED", False
            ),
        )
        return context
