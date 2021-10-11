from django.conf.urls import url

from .views import (
    LokaleOverheidDetailView,
    LokaleOverheidUpdateView,
    RoleCreateView,
    RoleDeleteView,
    RoleListView,
)

app_name = "organisaties"


urlpatterns = [
    # Municipality
    url(
        r"^overheid/(?P<pk>[\d]+)/$",
        LokaleOverheidDetailView.as_view(),
        name="overheid_detail",
    ),
    url(
        r"^overheid/(?P<pk>[\d]+)/edit/$",
        LokaleOverheidUpdateView.as_view(),
        name="overheid_edit",
    ),
    # Roles
    url(
        r"^overheid/(?P<pk>[\d]+)/roles/$",
        RoleListView.as_view(),
        name="overheid_roles",
    ),
    url(
        r"^overheid/(?P<pk>[\d]+)/roles/create$",
        RoleCreateView.as_view(),
        name="overheid_role_create",
    ),
    url(
        r"^overheid/(?P<pk>[\d]+)/roles/(?P<role_pk>[\d]+)/delete$",
        RoleDeleteView.as_view(),
        name="overheid_role_delete",
    ),
]
