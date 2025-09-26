from rest_framework import serializers
from .models import Rating


class RatingSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    content_id = serializers.IntegerField(source='content.id', read_only=True)
    user_nickname = serializers.CharField(source='user.user_nickname', read_only=True)

    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ('user', 'content', 'create_time', 'update_time')


class RatingCreateSerializer(serializers.Serializer):
    content_id = serializers.IntegerField(required=True)
    score = serializers.ChoiceField(
        choices=[(1.0, '1分'), (1.5, '1.5分'), (2.0, '2分'), (2.5, '2.5分'),
                (3.0, '3分'), (3.5, '3.5分'), (4.0, '4分'), (4.5, '4.5分'), (5.0, '5分')],
        required=True
    )

class RatingGetSerializer(serializers.Serializer):
    content_id = serializers.IntegerField(required=True)
