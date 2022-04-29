from django.urls import path, re_path

from sdg.organisaties.views import (
    InvitationCreateView,
    RoleDeleteView,
    RoleListView,
    RoleUpdateView,
)

app_name = "roles"
urlpatterns = [
    path("", RoleListView.as_view(), name="list"),
    path(r"invite/", InvitationCreateView.as_view(), name="invitation_create"),
    re_path(r"^(?P<role_pk>[\d]+)/update$", RoleUpdateView.as_view(), name="update"),
    re_path(r"^(?P<role_pk>[\d]+)/delete$", RoleDeleteView.as_view(), name="delete"),
]
