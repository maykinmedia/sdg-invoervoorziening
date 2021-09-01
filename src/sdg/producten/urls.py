from django.urls import path

from .views import ContactEditView, ProductDetailView, ProductListView

app_name = "producten"
urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("detail/1/", ProductDetailView.as_view(), name="detail"),
    path("edit/contact/", ContactEditView.as_view(), name="edit-contact"),
]
