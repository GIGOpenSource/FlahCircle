from rest_framework import viewsets
from follows.models import Follow
from follows.serializers import FollowSerializer


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
