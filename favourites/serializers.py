# user/serializers.py
from rest_framework import serializers
from favourites.models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'