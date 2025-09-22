from rest_framework import viewsets

from middleware.base_views import BaseViewSet
from tags.models import Tag
from tags.serializers import TagSerializer


class TagViewSet(BaseViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer