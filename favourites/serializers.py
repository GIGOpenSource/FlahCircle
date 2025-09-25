from rest_framework import serializers
from .models import Favorite, Downvote


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('user_id', 'user_nickname', 'target_title', 
                           'target_cover', 'target_author_id', 'create_time', 'update_time')

class FavoriteToggleSerializer(serializers.Serializer):
    target_id = serializers.IntegerField(required=True)


class DownvoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Downvote
        fields = '__all__'
        read_only_fields = ('user_id', 'user_nickname', 'target_title',
                           'target_cover', 'target_author_id', 'create_time', 'update_time')


class DownvoteToggleSerializer(serializers.Serializer):
    target_id = serializers.IntegerField(required=True)