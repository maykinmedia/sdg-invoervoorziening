from django.urls import include, path, re_path

from sdg.organisaties.views.catalogi import CatalogListView

app_name = "catalogi"
urlpatterns = [
    path("", CatalogListView.as_view(), name="list"),
    re_path(
        r"(?P<catalog_pk>[\d]+)/products/",
        include("sdg.producten.urls", namespace="producten"),
    ),
]
