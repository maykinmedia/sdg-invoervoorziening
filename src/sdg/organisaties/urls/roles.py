from django.conf.urls import url
from django.urls import path

from sdg.organisaties.views import RoleDeleteView, RoleListView, RoleUpdateView

app_name = "roles"
urlpatterns = [
    path("", RoleListView.as_view(), name="list"),
    url(r"^(?P<role_pk>[\d]+)/update$", RoleUpdateView.as_view(), name="update"),
    url(r"^(?P<role_pk>[\d]+)/delete$", RoleDeleteView.as_view(), name="delete"),
]
