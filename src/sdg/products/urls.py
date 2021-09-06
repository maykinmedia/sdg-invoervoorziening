from django.urls import path

from .views import ContactEditView, ProductDetailView, ProductEditView, ProductListView

app_name = "product"
urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("detail/1/", ProductDetailView.as_view(), name="detail"),
    path("edit/1/", ProductEditView.as_view(), name="edit"),
    path("edit/contact/", ContactEditView.as_view(), name="edit-contact"),
]
