from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from decorator_include import decorator_include

from sdg.accounts.tf_urls import urlpatterns as tf_urls
from sdg.decorators import enabled

handler500 = "sdg.utils.views.server_error"
admin.site.enable_nav_sidebar = False
admin.site.site_header = _("PDC voor de SDG")
admin.site.site_title = _("PDC voor de SDG")
admin.site.index_title = _("PDC beheer voor de SDG")

urlpatterns = [
    path("admin/", include("sdg.admin.urls")),
    path("api/", include("sdg.api.urls", namespace="api")),
    # cms - these urls can be disabled if desired though the setting SDG_CMS_ENABLED
    path("markdownx/", decorator_include(enabled(), "markdownx.urls")),
    path(
        "organizations/",
        decorator_include(enabled(), "sdg.organisaties.urls", namespace="organisaties"),
    ),
    path(
        "",
        decorator_include(enabled(redirect=True), "sdg.core.urls", namespace="core"),
    ),
    path(
        "cmsapi/",
        decorator_include(enabled(), "sdg.cmsapi.urls", namespace="cmsapi"),
    ),
    path("ref/", include("vng_api_common.urls")),
    # account urls:
    path(
        "account/",
        decorator_include(enabled(), "sdg.accounts.urls"),
    ),
    path("", decorator_include(enabled(), tf_urls)),
]


# NOTE: The staticfiles_urlpatterns also discovers static files (ie. no need to run collectstatic). Both the static
# folder and the media folder are only served via Django if DEBUG = True.
urlpatterns += staticfiles_urlpatterns() + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG and apps.is_installed("debug_toolbar"):
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
