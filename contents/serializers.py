# user/serializers.py
from rest_framework import serializers
from contents.models import Content


class ContentSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 格式化数值字段
        data['view_count'] = self.format_number(data.get('view_count', 0))
        data['like_count'] = self.format_number(data.get('like_count', 0))
        data['comment_count'] = self.format_number(data.get('comment_count', 0))
        data['favorite_count'] = self.format_number(data.get('favorite_count', 0))
        data['share_count'] = self.format_number(data.get('share_count', 0))
        data['score_count'] = self.format_number(data.get('score_count', 0))
        data['score_total'] = self.format_number(data.get('score_total', 0))
        return data

    def format_number(self, value):
        """格式化数字显示"""
        if not isinstance(value, (int, float)) or value is None:
            return value
        if value >= 10000000:  # 1000万
            return f"{value / 10000000:.1f}kw".replace('.0', '')
        elif value >= 10000:  # 1万
            return f"{value / 10000:.1f}w".replace('.0', '')
        elif value >= 1000:  # 1千
            return f"{value / 1000:.1f}k".replace('.0', '')
        else:
            return value

    class Meta:
        model = Content
        fields = '__all__'

class ContentWithFollowSerializer(serializers.ModelSerializer):
    is_follower = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favourites = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 格式化数值字段
        data['view_count'] = self.format_number(data.get('view_count', 0))
        data['like_count'] = self.format_number(data.get('like_count', 0))
        data['comment_count'] = self.format_number(data.get('comment_count', 0))
        data['favorite_count'] = self.format_number(data.get('favorite_count', 0))
        data['share_count'] = self.format_number(data.get('share_count', 0))
        data['score_count'] = self.format_number(data.get('score_count', 0))
        data['score_total'] = self.format_number(data.get('score_total', 0))
        return data

    def format_number(self, value):
        """格式化数字显示"""
        if not isinstance(value, (int, float)) or value is None:
            return value

        if value >= 10000000:  # 1000万
            return f"{value / 10000000:.1f}kw".replace('.0', '')
        elif value >= 10000:  # 1万
            return f"{value / 10000:.1f}w".replace('.0', '')
        elif value >= 1000:  # 1千
            return f"{value / 1000:.1f}k".replace('.0', '')
        else:
            return value

    class Meta:
        model = Content
        fields = '__all__'

    def get_is_follower(self, obj):
        """
        获取当前用户是否关注了该内容的作者
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # 从上下文中获取当前用户关注的用户ID列表
            followed_user_ids = self.context.get('followed_user_ids', [])
            # 注意：Content模型使用的是author_id而不是user_id
            return obj.author_id in followed_user_ids
        return False

    def get_is_liked(self, obj):
        """
        获取当前用户是否点赞了该内容
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            liked_dynamic_ids = self.context.get('liked_dynamic_ids', [])
            return obj.id in liked_dynamic_ids
        return False

    def get_is_favourites(self, obj):
        """
        获取当前用户是否收藏了该内容
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            favourite_dynamic_ids = self.context.get('favourite_dynamic_ids', [])
            return obj.id in favourite_dynamic_ids
        return False