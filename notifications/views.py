from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, filters

from middleware.base_views import BaseViewSet
from middleware.utils import CustomPagination, ApiResponse
from notifications.models import Notification
from notifications.serializers import NotificationSerializer, NotificationCreateSerializer
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
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_active']

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    # def get_queryset(self):
    #     """
    #     默认只返回当前登录用户的通知
    #     """
    #     queryset = super().get_queryset()
    #     if self.request.user.is_authenticated:
    #         queryset = queryset.filter(user=self.request.user)
    #     else:
    #         # 如果用户未登录，则不返回任何通知
    #         queryset = queryset.none()
    #     return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_ids = serializer.validated_data.get('user_ids', [])
        notifications = []

        if user_ids:
            # 为每个指定的用户创建通知
            for user_id in user_ids:
                notification_data = serializer.validated_data.copy()
                notification_data.pop('user_ids', None)
                notification_data['user_id'] = user_id
                notification = Notification.objects.create(**notification_data)
                notifications.append(notification)
        else:
            # 如果没有指定用户，创建一个通用通知（不关联特定用户）
            notification_data = serializer.validated_data.copy()
            notification_data.pop('user_ids', None)
            notification = Notification.objects.create(**notification_data)
            notifications.append(notification)

        # 序列化结果
        result_serializer = NotificationSerializer(notifications, many=True)
        return ApiResponse(result_serializer.data, message="创建成功", code=201)

    def list(self, request, *args, **kwargs):
        # 获取过滤后的查询集
        queryset = self.filter_queryset(self.get_queryset())
        # 获取分页器实例
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 使用自定义分页响应
            return self.get_paginated_response(serializer.data)
        # 如果没有分页，返回普通响应
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse(serializer.data)
