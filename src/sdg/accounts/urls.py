from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from sdg.accounts.views.password_reset import PasswordResetView
from sdg.organisaties.views import InvitationAcceptView

from .views.auth import LoginDashboardView

# app_name = "accounts"
urlpatterns = [
    path("login-dashboard/", LoginDashboardView.as_view(), name="login_dashboard"),
    path(
        "reset/",
        auth_views.PasswordResetView.as_view(
            template_name="account/password_reset.html"
        ),
        name="account_reset_password",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="account/password_reset_from_key.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset/",
        PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="account/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="account/password_reset_from_key_done.html"
        ),
        name="password_reset_complete",
    ),
    re_path(
        r"^invitation/(?P<key>\w+)/?$",
        InvitationAcceptView.as_view(),
        name="invitation_accept",
    ),
]
