from django.urls import path, include
from rest_framework.routers import DefaultRouter
from societies.views import DynamicViewSet, FollowedDynamicViewSet, InteractionMessageViewSet

router = DefaultRouter()
router.register(r'dynamic', DynamicViewSet)
router.register(r'dynamic_follow', FollowedDynamicViewSet, basename='followed-dynamic')
router.register(r'interaction_message', InteractionMessageViewSet, basename='interaction-message')

urlpatterns = [
    path('', include(router.urls)),
]