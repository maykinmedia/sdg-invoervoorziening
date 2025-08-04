from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from sdg.organisaties.views import InvitationAcceptView

from .views.auth import LoginDashboardView

app_name = "accounts"
urlpatterns = [
    path("login-dashboard/", LoginDashboardView.as_view(), name="login_dashboard"),
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
    re_path(
        r"^invitation/(?P<key>\w+)/?$",
        InvitationAcceptView.as_view(),
        name="invitation_accept",
    ),
]
