from rest_framework import viewsets
from likes.models import Like
from likes.serializers import LikeSerializer
from middleware.base_views import BaseViewSet


class LikeViewSet(BaseViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
