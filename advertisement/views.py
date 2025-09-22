from rest_framework import viewsets
from advertisement.models import Advertisement
from advertisement.serializers import AdvertisementSerializer


class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
