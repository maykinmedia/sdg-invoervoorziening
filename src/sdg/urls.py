from django.apps import apps
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.utils.translation import ugettext_lazy as _

from two_factor.urls import urlpatterns as tf_urls

from sdg.accounts.views.auth import LoginView
from sdg.accounts.views.password_reset import PasswordResetView
from sdg.organisaties.views import InvitationAcceptView

handler500 = "sdg.utils.views.server_error"
admin.site.site_header = _("SDG Invoervoorziening")
admin.site.site_title = _("SDG Invoervoorziening")
admin.site.index_title = _("Welkom bij de SDG-admin")

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
    path("admin/", admin.site.urls),
    path("markdownx/", include("markdownx.urls")),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    url(
        r"^accept-invitation/(?P<key>\w+)/?$",
        InvitationAcceptView.as_view(),
        name="invitation_accept",
    ),
    path("api/", include("sdg.api.urls", namespace="api")),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("sdg.accounts.urls", namespace="accounts")),
    path("organizations/", include("sdg.organisaties.urls", namespace="organisaties")),
    path("", include("sdg.core.urls", namespace="core")),
]

# two_factor
urlpatterns += [
    path("two_factor/login/", LoginView.as_view(), name="login"),  # custom
    path("", include(tf_urls)),
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
