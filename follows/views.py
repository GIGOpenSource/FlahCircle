from rest_framework import viewsets
from follows.models import Follow
from follows.serializers import FollowSerializer
from middleware.base_views import BaseViewSet


class FollowViewSet(BaseViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
