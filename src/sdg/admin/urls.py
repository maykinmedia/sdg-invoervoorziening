from django.contrib import admin
from django.urls import include, path

from maykin_2fa import monkeypatch_admin
from maykin_2fa.urls import urlpatterns, webauthn_urlpatterns

from sdg.accounts.views.password_reset import ResendInventation

# Configure admin

monkeypatch_admin()

urlpatterns = [
    path("hijack/", include("hijack.urls")),
    path("resend_invite", ResendInventation.as_view(), name="resend_token"),
    path("", include((urlpatterns, "maykin_2fa"))),
    path("", include((webauthn_urlpatterns, "admin_two_factor"))),
    path("", admin.site.urls),
]
