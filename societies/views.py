from rest_framework import viewsets

from middleware.base_views import BaseViewSet
from societies.models import Dynamic
from societies.serializers import SocialDynamicSerializer


class DynamicViewSet(BaseViewSet):
    queryset = Dynamic.objects.all()
    serializer_class = SocialDynamicSerializer