from rest_framework import serializers
from likes.models import Like

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ('user_id', 'user_nickname', 'user_avatar',
                           'target_author_id', 'target_title', 'create_time', 'update_time')

class LikeToggleSerializer(serializers.Serializer):
    target_id = serializers.IntegerField(required=True)