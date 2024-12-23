from django.urls import path

from sdg.organisaties.views.notificaties import ProductVersieListView

app_name = "notificaties"
urlpatterns = [
    path("", ProductVersieListView.as_view(), name="list"),
]