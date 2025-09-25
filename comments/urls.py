from django.urls import path, include
from rest_framework.routers import DefaultRouter
from comments.views import CommentViewSet, ContentCommentViewSet, DynamicCommentViewSet

router = DefaultRouter()

router.register(r'v1', ContentCommentViewSet, basename='content-comment')
router.register(r'v2', DynamicCommentViewSet, basename='dynamic-comment')

urlpatterns = [
    path('', include(router.urls)),
]