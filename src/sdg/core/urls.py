from django.urls import include, path

from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]
