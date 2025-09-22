# user/serializers.py
from rest_framework import serializers
from messages.models import Message, Session, Settings


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = '__all__'


class SettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = '__all__'