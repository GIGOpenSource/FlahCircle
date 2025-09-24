from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from chat.models import Message, Session, Settings
from chat.serializers import MessageSerializer, SessionSerializer, SettingsSerializer
from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse


@extend_schema_view(
    list=extend_schema(summary='获取消息列表 通过receiver_id 聊天室id返回所有对话', tags=['聊天室功能']),
    retrieve=extend_schema(summary='获取消息详情', tags=['聊天室功能']),
    create=extend_schema(summary='创建消息', tags=['聊天室功能']),
    update=extend_schema(summary='更新消息', tags=['聊天室功能']),
    partial_update=extend_schema(summary='部分更新消息', tags=['聊天室功能']),
    destroy=extend_schema(summary='删除消息', tags=['聊天室功能'])
)
class MessageViewSet(BaseViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['receiver_id', 'sender_id', 'type','reply_to_id']
    ordering_fields = ['create_time']
    ordering = ['create_time']

    def perform_create(self, serializer):
        # 自动设置发送者ID为当前登录用户
        serializer.save(sender_id=self.request.user.id)

    @extend_schema(summary='发送消息', tags=['聊天室功能'])
    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request):
        """
        发送消息
        必传当前房间的receiver_id字段，且传来的receiver_id字段必须在t_message_session表中的session_id里
        sender_id为自己，reply_to_id为传的值
        """
        # 获取当前用户ID（发送者）
        sender_id = request.user.id

        # 获取必需参数
        receiver_id = request.data.get('receiver_id')
        content = request.data.get('content')
        message_type = request.data.get('type', 'text')
        extra_data = request.data.get('extra_data', {})
        reply_to_id = request.data.get('reply_to_id')

        # 验证必需参数
        if not receiver_id:
            return ApiResponse(code=400, message="缺少接收者ID")

        if not content:
            return ApiResponse(code=400, message="消息内容不能为空")

        session_exists = Session.objects.filter(session_id=receiver_id).exists()
        if not session_exists:
            return ApiResponse(code=400, message="房间不存在或已解散")

        # 创建消息
        message = Message.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            type=message_type,
            extra_data=extra_data,
            reply_to_id=reply_to_id
        )

        # 序列化返回
        serializer = MessageSerializer(message)
        return ApiResponse(serializer.data, message="消息发送成功")


@extend_schema_view(
    list=extend_schema(summary='获取会话',tags=['会话管理'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取会话详情',tags=['会话管理']),
    # create=extend_schema(summary='创建会话',tags=['会话管理']),
    # update=extend_schema(summary='更新会话',tags=['会话管理']),
    # partial_update=extend_schema(summary='部分更新会话',tags=['会话管理']),
    destroy=extend_schema(summary='删除会话',tags=['会话管理'])
)
class SessionViewSet(BaseViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    @extend_schema(summary='创建会话房间', tags=['聊天室功能'])
    @action(detail=False, methods=['post'], url_path='create-room')
    def create_room(self, request):
        """
        创建会话房间
        通过Token获取userid，以及传来的other_user_id创建房间
        session_id作为聊天功能的receiver_id关联
        """
        # 通过Token获取当前用户ID
        current_user_id = request.user.id

        # 获取传来的other_user_id
        other_user_id = request.data.get('other_user_id')

        if not other_user_id:
            return ApiResponse(code=400, message="缺少对方用户ID")

        try:
            other_user_id = int(other_user_id)
        except (ValueError, TypeError):
            return ApiResponse(code=400, message="对方用户ID必须为数字")

        # 验证对方用户是否存在
        try:
            from user.models import User
            User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return ApiResponse(code=400, message="对方用户不存在")

        # 检查是否已经存在会话（检查两个方向）
        existing_session = Session.objects.filter(
            user_id=current_user_id,
            other_user_id=other_user_id
        ).first()

        if existing_session:
            return ApiResponse({
                'session_id': existing_session.session_id,
                'participants': [current_user_id, other_user_id]
            }, message="会话已存在")

        # 生成唯一的会话ID
        import time
        session_id = str(int(time.time() * 1000000)) + "_" + get_random_string(8)

        # 只创建一个会话记录（当前用户视角）
        session = Session.objects.create(
            user_id=current_user_id,
            other_user_id=other_user_id,
            session_id=session_id,
            session_type='private'
        )

        # 返回会话信息
        return ApiResponse({
            'session_id': session_id,
            'participants': [current_user_id, other_user_id]
        }, message="会话房间创建成功")


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
