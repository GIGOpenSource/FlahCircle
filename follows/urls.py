from django.urls import path, include
from rest_framework.routers import DefaultRouter
from follows.views import FollowViewSet

router = DefaultRouter()
router.register(r'v2', FollowViewSet)

urlpatterns = [
    path('', include(router.urls)),
]