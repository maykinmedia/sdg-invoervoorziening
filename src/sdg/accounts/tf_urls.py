from django.urls import path

from two_factor.urls import urlpatterns as tf_urlpatterns

from .views.auth import LoginView, LogoutView


def get_two_factor_urls():
    assert isinstance(tf_urlpatterns, (list, tuple))
    assert isinstance(tf_urlpatterns[0], (list, tuple))
    url_list = []

    for url in tf_urlpatterns[0]:
        if hasattr(url, "name") and url.name == "login":
            continue

        url_list.append(url)

    return url_list


custom_urls = [
    path(
        "account/login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "account/logout/",
        LogoutView.as_view(),
        name="logout",
    ),
]

urlpatterns = (custom_urls + get_two_factor_urls(), "two_factor")
