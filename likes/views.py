from rest_framework import viewsets
from likes.models import Like
from likes.serializers import LikeSerializer


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
