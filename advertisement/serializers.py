# user/serializers.py
from rest_framework import serializers
from advertisement.models import Advertisement


class AdvertisementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Advertisement
        fields = '__all__'