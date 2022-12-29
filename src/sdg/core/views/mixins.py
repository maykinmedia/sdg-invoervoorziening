from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
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


class BreadcrumbsMixin(ContextMixin):
    """
    Allow further customization of the breadcrumbs.
    """

    breadcrumbs_title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            breadcrumbs_title=self.get_breadcrumbs_title(),
        )
        return context

    def get_breadcrumbs_title(self):
        """
        Return the breadcrumbs page title.
        Raise an exception if the breadcrumbs_title is not set.
        """
        if self.breadcrumbs_title is None:
            cls_name = self.__class__.__name__
            raise ImproperlyConfigured(
                f"{cls_name} requires either a definition of "
                "'breadcrumbs_title' or an implementation of "
                "'get_breadcrumbs_title()'"
            )

        return self.breadcrumbs_title
