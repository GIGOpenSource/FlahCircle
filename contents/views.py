from rest_framework import viewsets
from contents.models import Content
from contents.serializers import ContentSerializer


class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
