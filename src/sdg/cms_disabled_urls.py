from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.utils.translation import gettext_lazy as _

from sdg.accounts.views.password_reset import PasswordResetView

handler500 = "sdg.utils.views.server_error"
admin.site.site_header = _("SDG Invoervoorziening")
admin.site.site_title = _("SDG Invoervoorziening")
admin.site.index_title = _("Welkom bij de SDG-admin")
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
    path("admin/", admin.site.urls),
    path("api/", include("sdg.api.urls", namespace="api")),
]

# NOTE: The staticfiles_urlpatterns also discovers static files (ie. no need to run collectstatic). Both the static
# folder and the media folder are only served via Django if DEBUG = True.
urlpatterns += staticfiles_urlpatterns() + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
