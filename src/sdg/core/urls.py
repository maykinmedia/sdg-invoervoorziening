from django.urls import include, path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]

# TODO: log CMS
# location (save)
# product (save/publish)
