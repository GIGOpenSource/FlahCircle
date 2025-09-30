# user/serializers.py
from rest_framework import serializers
from notifications.models import Notification
from user.models import User


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_nickname', 'avatar', 'username', 'is_vip']  # 添加 username 和 is_vip 字段


class NotificationSerializer(serializers.ModelSerializer):
    user = UserNotificationSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'


class NotificationCreateSerializer(serializers.ModelSerializer):
    # 支持单个用户ID或多个用户ID
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="用户ID列表，支持多个用户"
    )

    class Meta:
        model = Notification
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }
