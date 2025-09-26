from rest_framework import serializers
from tags.models import Tag
from user.models import User

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

class UserRecommendationSerializer(serializers.ModelSerializer):
    """
    用户推荐序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'user_nickname', 'avatar', 'followers_count', 'following_count', 'is_vip']