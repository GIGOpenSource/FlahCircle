from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('user_id', 'user_nickname', 'user_avatar',
                           'reply_to_user_id', 'reply_to_user_nickname', 'reply_to_user_avatar',
                           'like_count', 'reply_count', 'create_time', 'update_time','prefixed_id')
    
    def get_is_liked(self, obj):
        """
        获取当前用户是否点赞了该评论
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            liked_comment_ids = self.context.get('liked_comment_ids', [])
            return obj.id in liked_comment_ids
        return False
