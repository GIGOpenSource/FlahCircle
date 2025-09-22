from django.urls import path, include
from rest_framework.routers import DefaultRouter
from societies.views import DynamicViewSet

router = DefaultRouter()
router.register(r'dynamic', DynamicViewSet)

urlpatterns = [
    path('', include(router.urls)),
]