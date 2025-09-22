from rest_framework import viewsets
from goods.models import Good
from goods.serializers import GoodSerializer
from middleware.base_views import BaseViewSet


class GoodViewSet(BaseViewSet):
    queryset = Good.objects.all()
    serializer_class = GoodSerializer
