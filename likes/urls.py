from django.urls import path, include
from rest_framework.routers import DefaultRouter
from likes.views import DynamicLikeViewSet, ContentLikeViewSet

router = DefaultRouter()
# router.register(r'', ContentLikeViewSet)
router.register(r'v1/content', ContentLikeViewSet, basename='content-like')
router.register(r'v2/dynamic', DynamicLikeViewSet, basename='dynamic-like')


urlpatterns = [
    path('', include(router.urls)),
]