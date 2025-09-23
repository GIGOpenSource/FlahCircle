from rest_framework import viewsets

from middleware.base_views import BaseViewSet
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

@extend_schema_view(
    list=extend_schema(summary='获取消息/通知',tags=['消息中心'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取消息/通知详情',tags=['消息中心']),
    create=extend_schema(summary='创建消息/通知',tags=['消息中心']),
    update=extend_schema(summary='更新消息/通知',tags=['消息中心']),
    partial_update=extend_schema(summary='部分更新消息/通知',tags=['消息中心']),
    destroy=extend_schema(summary='删除消息/通知',tags=['消息中心'])
)
class NotificationViewSet(BaseViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
