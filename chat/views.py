from rest_framework import viewsets
from chat.models import Message, Session, Settings
from chat.serializers import MessageSerializer, SessionSerializer, SettingsSerializer
from middleware.base_views import BaseViewSet


class MessageViewSet(BaseViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class SessionViewSet(BaseViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class SettingsViewSet(BaseViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
