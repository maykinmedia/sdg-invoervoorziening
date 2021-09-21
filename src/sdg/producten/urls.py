from django.conf.urls import url

from sdg.producten.views.product import ProductDetailView, ProductUpdateView

app_name = "producten"
urlpatterns = [
    url(
        r"^(?P<pk>\d+)/$",
        ProductDetailView.as_view(),
        name="detail",
    ),
    url(r"^(?P<pk>\d+)/edit/$", ProductUpdateView.as_view(), name="edit"),
]
