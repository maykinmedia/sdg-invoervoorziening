from django.urls import re_path

from sdg.organisaties.views import LokaleOverheidUpdateView
from sdg.organisaties.views.bevoegde_organisaties import BevoegdeOrganisatieUpdateView
from sdg.organisaties.views.locaties import LocatieUpdateView

urlpatterns = [
    re_path(
        r"^(?P<pk>[\d]+)/edit/$",
        LokaleOverheidUpdateView.as_view(),
        name="edit",
    ),
    re_path(
        r"^(?P<pk>[\d]+)/locaties/",
        LocatieUpdateView.as_view(),
        name="locaties",
    ),
    re_path(
        r"^(?P<pk>[\d]+)/bevoegde-organisaties/",
        BevoegdeOrganisatieUpdateView.as_view(),
        name="bevoegde_organisaties",
    ),
]
