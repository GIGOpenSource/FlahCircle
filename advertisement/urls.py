from django.urls import path, include
from rest_framework.routers import DefaultRouter
from advertisement.views import AdvertisementViewSet

router = DefaultRouter()
router.register(r'', AdvertisementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]