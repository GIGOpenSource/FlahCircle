from rest_framework import viewsets
from societies.models import Dynamic
from societies.serializers import SocialDynamicSerializer


class DynamicViewSet(viewsets.ModelViewSet):
    queryset = Dynamic.objects.all()
    serializer_class = SocialDynamicSerializer