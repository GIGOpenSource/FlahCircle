from rest_framework import viewsets
from goods.models import Good
from goods.serializers import GoodSerializer


class GoodViewSet(viewsets.ModelViewSet):
    queryset = Good.objects.all()
    serializer_class = GoodSerializer
