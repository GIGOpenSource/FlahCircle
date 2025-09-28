from rest_framework import serializers
from chat.models import Message, Session, Settings


class MessageSerializer(serializers.ModelSerializer):
    sender_nickname = serializers.SerializerMethodField()
    sender_avatar = serializers.SerializerMethodField()
    receiver_nickname = serializers.SerializerMethodField()
    receiver_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('sender_id', 'create_time', 'update_time')

    def get_sender_nickname(self, obj):
        if obj.sender_id:
            try:
                from user.models import User
                user = User.objects.get(id=obj.sender_id)
                return user.user_nickname
            except User.DoesNotExist:
                return None
        return None

    def get_sender_avatar(self, obj):
        if obj.sender_id:
            try:
                from user.models import User
                user = User.objects.get(id=obj.sender_id)
                if user.avatar:
                    # 如果avatar是字符串URL，则直接返回；否则尝试获取url属性
                    if isinstance(user.avatar, str):
                        return user.avatar
                    else:
                        return getattr(user.avatar, 'url', None)
                return None
            except User.DoesNotExist:
                return None
        return None

    def get_receiver_nickname(self, obj):
        if obj.receiver_id:
            try:
                from user.models import User
                user = User.objects.get(id=obj.receiver_id)
                return user.user_nickname
            except User.DoesNotExist:
                return None
            except:
                return None
        return None

    def get_receiver_avatar(self, obj):
        if obj.receiver_id:
            try:
                from user.models import User
                user = User.objects.get(id=obj.receiver_id)
                # 修复：检查avatar是否存在且有url属性
                if user.avatar:
                    # 如果avatar是字符串URL，则直接返回；否则尝试获取url属性
                    if isinstance(user.avatar, str):
                        return user.avatar
                    else:
                        return getattr(user.avatar, 'url', None)
                return None
            except User.DoesNotExist:
                return None
            except:
                return None
        return None


class SessionSerializer(serializers.ModelSerializer):
    other_user_nickname = serializers.SerializerMethodField()
    other_user_avatar = serializers.SerializerMethodField()
    last_message_content = serializers.SerializerMethodField()
    user_nickname = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    class Meta:
        model = Session
        fields = '__all__'
        read_only_fields = ('user_id', 'create_time', 'update_time')

    def get_other_user_nickname(self, obj):
        if obj.other_user_id:
            try:
                from user.models import User
                user = User.objects.get(id=obj.other_user_id)
                return user.user_nickname
            except User.DoesNotExist:
                return None
        return None

    def get_other_user_avatar(self, obj):
        if obj.other_user_id:
            try:
                from user.models import User
                user = User.objects.get(id=obj.other_user_id)
                # 修复：检查avatar是否存在且有url属性
                if user.avatar:
                    # 如果avatar是字符串URL，则直接返回；否则尝试获取url属性
                    if isinstance(user.avatar, str):
                        return user.avatar
                    else:
                        return getattr(user.avatar, 'url', None)
                return None
            except User.DoesNotExist:
                return None
        return None

    def get_user_nickname(self, obj):
        if obj.user_id:
            try:
                from user.models import User
                user = User.objects.get(id=obj.user_id)
                return user.user_nickname
            except User.DoesNotExist:
                return None
        return None

    def get_user_avatar(self, obj):
        if obj.user_id:
            try:
                from user.models import User
                user = User.objects.get(id=obj.user_id)
                if user.avatar:
                    # 如果avatar是字符串URL，则直接返回；否则尝试获取url属性
                    if isinstance(user.avatar, str):
                        return user.avatar
                    else:
                        return getattr(user.avatar, 'url', None)
                return None
            except User.DoesNotExist:
                return None
        return None

    def get_last_message_content(self, obj):
        if obj.last_message_id:
            try:
                message = Message.objects.get(id=obj.last_message_id)
                return message.content
            except Message.DoesNotExist:
                return None
        return None

    def get_last_message(self, obj):
        """
        获取会话的最后一条消息
        通过session_id匹配message表的receiver_id，按时间倒序返回最后一条
        """
        if obj.session_id:
            try:
                # 获取receiver_id等于session_id的最后一条消息
                last_message = Message.objects.filter(
                    receiver_id=obj.session_id
                ).order_by('-create_time').first()

                if last_message:
                    return MessageSerializer(last_message).data
                return None
            except Exception:
                return None
        return None

class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = '__all__'
        read_only_fields = ('user_id', 'create_time', 'update_time')
