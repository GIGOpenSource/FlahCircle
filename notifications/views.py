from rest_framework import viewsets

from middleware.base_views import BaseViewSet
from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationViewSet(BaseViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
