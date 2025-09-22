# user/serializers.py
from rest_framework import serializers
from goods.models import Good


class GoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Good
        fields = '__all__'