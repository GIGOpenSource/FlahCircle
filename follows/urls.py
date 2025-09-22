from django.urls import path, include
from rest_framework.routers import DefaultRouter
from follows.views import FollowViewSet

router = DefaultRouter()
router.register(r'', FollowViewSet)

urlpatterns = [
    path('', include(router.urls)),
]