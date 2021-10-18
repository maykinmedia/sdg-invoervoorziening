from django.conf.urls import url

from .views import (
    InvitationAcceptView,
    InvitationCreateView,
    LokaleOverheidDetailView,
    LokaleOverheidUpdateView,
    RoleCreateView,
    RoleDeleteView,
    RoleListView,
    RoleUpdateView,
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
        r"^overheid/(?P<pk>[\d]+)/roles/(?P<role_pk>[\d]+)/update$",
        RoleUpdateView.as_view(),
        name="overheid_role_update",
    ),
    url(
        r"^overheid/(?P<pk>[\d]+)/roles/(?P<role_pk>[\d]+)/delete$",
        RoleDeleteView.as_view(),
        name="overheid_role_delete",
    ),
    # Invitation
    url(
        r"^overheid/(?P<pk>[\d]+)/invite/$",
        InvitationCreateView.as_view(),
        name="invitation_create",
    ),
    url(
        r"^accept-invitation/(?P<key>\w+)/?$",
        InvitationAcceptView.as_view(),
        name="invitation_accept",
    ),
]
