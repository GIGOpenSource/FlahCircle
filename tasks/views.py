from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse
from tasks.models import Reward, Template
from tasks.serializers import TaskRewardSerializer, TaskTemplateSerializer


@extend_schema_view(
    list=extend_schema(
        summary='获取任务奖励列表（分页)',
        tags=['任务奖励管理'],
        parameters=[
            OpenApiParameter(name='status', description='任务奖励状态过滤: pending(待领取), claimed(已领取), completed(已完成)', required=False),
            OpenApiParameter(name='type', description='任务奖励类型过滤: daily(每日任务), checkin(签到任务), novice(新手任务)', required=False)
        ]
    ),
    retrieve=extend_schema(summary='获取任务奖励详情', tags=['任务奖励管理']),
    create=extend_schema(summary='创建任务奖励（后台）', tags=['任务奖励管理']),
    update=extend_schema(summary='更新任务奖励（后台）', tags=['任务奖励管理']),
    partial_update=extend_schema(summary='部分更新任务奖励（后台）', tags=['任务奖励管理']),
    destroy=extend_schema(summary='删除任务奖励（后台）', tags=['任务奖励管理'])
)
class RewardViewSet(BaseViewSet):
    queryset = Reward.objects.all()
    serializer_class = TaskRewardSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            # 只返回当前用户的任务奖励
            queryset = queryset.filter(user=self.request.user)
        return queryset

    @extend_schema(
        summary='领取任务奖励',
        tags=['任务奖励管理'],
        responses={200: TaskRewardSerializer}
    )
    @action(detail=True, methods=['post'], url_path='claim')
    def claim_reward(self, request, pk=None):
        """
        领取任务奖励接口
        用户领取已分发的任务奖励
        """
        if not request.user.is_authenticated:
            return ApiResponse(code=401, message="用户未登录")

        reward = self.get_object()

        # 检查是否是当前用户的任务
        if reward.user != request.user:
            return ApiResponse(code=403, message="无权限操作此任务")

        # 检查任务状态是否为待领取
        if reward.status != 'pending':
            return ApiResponse(code=400, message="任务状态不允许领取")

        # 更新任务状态为已领取
        try:
            reward.status = 'claimed'
            reward.save(update_fields=['status', 'update_time'])

            serializer = TaskRewardSerializer(reward)
            return ApiResponse(
                data=serializer.data,
                message="任务领取成功",
                code=200
            )
        except Exception as e:
            return ApiResponse(code=500, message=f"任务领取失败: {str(e)}")

    def perform_create(self, serializer):
        # 后台创建任务奖励时自动设置创建时间
        serializer.save()


@extend_schema_view(
    list=extend_schema(
        summary='获取任务模板列表（分页)',
        tags=['任务模板管理'],
        parameters=[
            OpenApiParameter(name='type', description='任务模板类型过滤: daily(每日任务), checkin(签到任务), novice(新手任务)', required=False),
            OpenApiParameter(name='is_active', description='任务模板是否激活过滤: true(激活), false(未激活)', required=False)
        ]
    ),
    retrieve=extend_schema(summary='获取任务模板详情', tags=['任务模板管理']),
    create=extend_schema(summary='创建任务模板（后台）', tags=['任务模板管理']),
    update=extend_schema(summary='更新任务模板（后台）', tags=['任务模板管理']),
    partial_update=extend_schema(summary='部分更新任务模板（后台）', tags=['任务模板管理']),
    destroy=extend_schema(summary='删除任务模板（后台）', tags=['任务模板管理'])
)
class TemplateViewSet(BaseViewSet):
    queryset = Template.objects.all()
    serializer_class = TaskTemplateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = TaskTemplateSerializer(instance=queryset, many=True)
        return ApiResponse(code=200, data=serializer.data, message="任务模板列表获取成功")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TaskTemplateSerializer(instance=instance)
        return ApiResponse(code=200, data=serializer.data, message="任务模板详情获取成功")
