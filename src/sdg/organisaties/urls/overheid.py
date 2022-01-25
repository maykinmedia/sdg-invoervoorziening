from django.conf.urls import url

from sdg.organisaties.views import InvitationCreateView, LokaleOverheidUpdateView

urlpatterns = [
    url(
        r"^(?P<pk>[\d]+)/edit/$",
        LokaleOverheidUpdateView.as_view(),
        name="edit",
    ),
]
