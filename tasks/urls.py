from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import RewardViewSet, TemplateViewSet

router = DefaultRouter()
router.register(r'reward', RewardViewSet)
router.register(r'template', TemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]