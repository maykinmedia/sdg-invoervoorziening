from django.conf.urls import url
from django.urls import include, path

from sdg.organisaties.views.catalogi import CatalogListView

app_name = "catalogi"
urlpatterns = [
    path("", CatalogListView.as_view(), name="list"),
    url(
        r"(?P<catalog_pk>[\d]+)/products/",
        include("sdg.producten.urls", namespace="producten"),
    ),
]
