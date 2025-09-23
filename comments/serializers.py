
from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('user_id', 'user_nickname', 'user_avatar',
                           'reply_to_user_id', 'reply_to_user_nickname', 'reply_to_user_avatar',
                           'like_count', 'reply_count', 'create_time', 'update_time')