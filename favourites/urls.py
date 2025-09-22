from django.urls import path, include
from rest_framework.routers import DefaultRouter
from favourites.views import FavoriteViewSet

router = DefaultRouter()
router.register(r'', FavoriteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]