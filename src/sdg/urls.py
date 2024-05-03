from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from decorator_include import decorator_include
from maykin_2fa import monkeypatch_admin
from maykin_2fa.urls import urlpatterns, webauthn_urlpatterns
from two_factor.urls import urlpatterns as tf_urls

from sdg import miscellaneous_urls
from sdg.accounts.views.password_reset import PasswordResetView, ResendInventation
from sdg.decorators import enabled
from sdg.organisaties.views.notificaties import ProductVersieListView

# Configure admin
monkeypatch_admin()

handler500 = "sdg.utils.views.server_error"
admin.site.site_header = _("PDC voor de SDG")
admin.site.site_title = _("PDC voor de SDG")
admin.site.index_title = _("PDC beheer voor de SDG")
admin.site.enable_nav_sidebar = False


urlpatterns = [
    path(
        "admin/password_reset/",
        PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path("admin/hijack/", include("hijack.urls")),
    path("admin/resend_invite", ResendInventation.as_view(), name="resend_token"),
    path("admin/", include((urlpatterns, "maykin_2fa"))),
    path("admin/", include((webauthn_urlpatterns, "admin_two_factor"))),
    path("admin/", admin.site.urls),
    path("api/", include("sdg.api.urls", namespace="api")),
    # cms - these urls can be disabled if desired though the setting SDG_CMS_ENABLED
    path("markdownx/", decorator_include(enabled(), "markdownx.urls")),
    path("accounts/", decorator_include(enabled(), "allauth.urls")),
    path(
        "accounts/",
        decorator_include(enabled(), "sdg.accounts.urls", namespace="accounts"),
    ),
    path(
        "organizations/",
        decorator_include(enabled(), "sdg.organisaties.urls", namespace="organisaties"),
    ),
    path(
        "notifications/",
        ProductVersieListView.as_view(),
        name="notificaties",
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
    path("", decorator_include(enabled(), miscellaneous_urls)),
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
