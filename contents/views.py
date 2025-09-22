from rest_framework import viewsets
from contents.models import Content
from contents.serializers import ContentSerializer
from middleware.base_views import BaseViewSet


class ContentViewSet(BaseViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
