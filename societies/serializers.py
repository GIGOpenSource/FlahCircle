from rest_framework import serializers
from societies.models import Dynamic


class SocialDynamicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dynamic
        fields = '__all__'
        read_only_fields = ('prefixed_id',)

class SocialDynamicWithFollowSerializer(serializers.ModelSerializer):
    is_follower = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favourites = serializers.SerializerMethodField()

    class Meta:
        model = Dynamic
        fields = '__all__'

    def get_is_follower(self, obj):
        """
        获取当前用户是否关注了该动态的作者
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # 从上下文中获取当前用户关注的用户ID列表
            followed_user_ids = self.context.get('followed_user_ids', [])
            return obj.user_id in followed_user_ids
        return False

    def get_is_liked(self, obj):
        """
        获取当前用户是否点赞了该动态
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            liked_dynamic_ids = self.context.get('liked_dynamic_ids', [])
            return obj.id in liked_dynamic_ids
        return False

    def get_is_favourites(self, obj):
        """
        获取当前用户是否收藏了该动态
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            favourite_dynamic_ids = self.context.get('favourite_dynamic_ids', [])
            return obj.id in favourite_dynamic_ids
        return False
