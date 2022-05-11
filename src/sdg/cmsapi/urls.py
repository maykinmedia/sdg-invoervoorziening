from django.urls import include, path
from rest_framework import routers
from sdg.cmsapi import views

app_name = "cmsapi"

router = routers.DefaultRouter(trailing_slash=False)
router.register("translation/", views.ProductTranslation)

urlpatterns = [
    path("", include(router.urls)),
]
