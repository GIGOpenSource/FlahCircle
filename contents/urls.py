from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contents.views import ContentViewSet

router = DefaultRouter()
router.register(r'', ContentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]