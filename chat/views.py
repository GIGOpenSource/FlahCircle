from rest_framework import viewsets
from chat.models import Message, Session, Settings
from chat.serializers import MessageSerializer, SessionSerializer, SettingsSerializer
from middleware.base_views import BaseViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
@extend_schema_view(
    list=extend_schema(summary='获取消息',tags=['会话管理'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取消息详情',tags=['会话管理']),
    create=extend_schema(summary='创建消息',tags=['会话管理']),
    update=extend_schema(summary='更新消息',tags=['会话管理']),
    partial_update=extend_schema(summary='部分更新消息',tags=['会话管理']),
    destroy=extend_schema(summary='删除消息',tags=['会话管理'])
)
class MessageViewSet(BaseViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

@extend_schema_view(
    list=extend_schema(summary='获取会话',tags=['会话管理'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取会话详情',tags=['会话管理']),
    create=extend_schema(summary='创建会话',tags=['会话管理']),
    update=extend_schema(summary='更新会话',tags=['会话管理']),
    partial_update=extend_schema(summary='部分更新会话',tags=['会话管理']),
    destroy=extend_schema(summary='删除会话',tags=['会话管理'])
)
class SessionViewSet(BaseViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

@extend_schema_view(
    list=extend_schema(summary='获取会话设置',tags=['会话管理'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取会话设置详情',tags=['会话管理']),
    create=extend_schema(summary='创建会话设置',tags=['会话管理']),
    update=extend_schema(summary='更新会话设置',tags=['会话管理']),
    partial_update=extend_schema(summary='部分更新会话设置',tags=['会话管理']),
    destroy=extend_schema(summary='删除会话设置',tags=['会话管理'])
)
class SettingsViewSet(BaseViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
