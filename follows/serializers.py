# user/serializers.py
from rest_framework import serializers
from follows.models import Follow


from rest_framework import serializers
from follows.models import Follow

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'
        read_only_fields = ('follower_id', 'follower_nickname', 'follower_avatar',
                           'followee_nickname', 'followee_avatar', 'create_time', 'update_time')

class FollowToggleSerializer(serializers.Serializer):
    followee_id = serializers.IntegerField(required=True)