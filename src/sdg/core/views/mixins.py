from django.conf import settings
from django.views.generic.base import ContextMixin

from sdg.conf.utils import org_type_cfg


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
            org_type_cfg=org_type_cfg(),
        )
        return context
