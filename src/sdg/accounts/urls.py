from django.urls import path

from sdg.accounts.views.auth import LoginDashboardView

app_name = "accounts"
urlpatterns = [
    path("login-dashboard/", LoginDashboardView.as_view(), name="login_dashboard"),
]
