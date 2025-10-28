from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ai_comment.serializers import AIConfigSerializer
from ai_comment.views import AIConfigViewSet

router = DefaultRouter()

router.register(r'configs', AIConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
]