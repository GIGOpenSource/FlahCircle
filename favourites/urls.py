from django.urls import path, include
from rest_framework.routers import DefaultRouter
from favourites.views import DynamicFavoriteViewSet, ContentFavoriteViewSet, DownvoteViewSet

router = DefaultRouter()
# router.register(r'', DynamicFavoriteViewSet)


# ContentFavoriteViewSet 内容收藏
router.register(r'v1', ContentFavoriteViewSet, basename='content-favorite')
# DynamicFavoriteViewSet 动态收藏
router.register(r'v2', DynamicFavoriteViewSet, basename='dynamic-favorite')
router.register(r'v1/downvote', DownvoteViewSet, basename='downvote')
urlpatterns = [
    path('', include(router.urls)),
]