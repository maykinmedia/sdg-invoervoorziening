from django.conf.urls import url
from django.contrib.auth import views as auth_views


app_name = "accounts"
urlpatterns = [
    url(
        r"^login/$",
        auth_views.LoginView.as_view(template_name="pages/index.html"),
        name="login",
    ),
    url(
        r"^logout/$", auth_views.LogoutView.as_view(), {"next_page": "/"}, name="logout"
    ),
]
