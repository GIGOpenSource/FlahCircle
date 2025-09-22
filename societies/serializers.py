# user/serializers.py
from rest_framework import serializers
from societies.models import Dynamic


class SocialDynamicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dynamic
        fields = '__all__'