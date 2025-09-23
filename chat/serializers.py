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
                return user.avatar.url if user.avatar else None
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
                return user.avatar.url if user.avatar else None
            except User.DoesNotExist:
                return None
            except:
                return None
        return None


class SessionSerializer(serializers.ModelSerializer):
    other_user_nickname = serializers.SerializerMethodField()
    other_user_avatar = serializers.SerializerMethodField()
    last_message_content = serializers.SerializerMethodField()

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
                return user.avatar.url if user.avatar else None
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


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = '__all__'
        read_only_fields = ('user_id', 'create_time', 'update_time')
