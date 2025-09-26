from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contents.views import ContentViewSet, FollowedContentViewSet

router = DefaultRouter()

router.register(r'content_follow', FollowedContentViewSet, basename='followed-content')
router.register(r'', ContentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]