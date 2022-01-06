from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "core"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]
