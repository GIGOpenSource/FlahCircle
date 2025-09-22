from rest_framework import viewsets
from favourites.models import Favorite
from favourites.serializers import FavoriteSerializer
from middleware.base_views import BaseViewSet


class FavoriteViewSet(BaseViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
