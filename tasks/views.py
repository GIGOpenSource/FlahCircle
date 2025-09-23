
from rest_framework import viewsets

from middleware.utils import ApiResponse
from tasks.models import Reward, Template
from tasks.serializers import TaskRewardSerializer, TaskTemplateSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter


@extend_schema_view(
    list=extend_schema(summary='获取奖励任务列表（分页)',tags=['奖励任务管理'],
        parameters=[OpenApiParameter(name='follower_id', description='奖励任务类型过滤'),
        OpenApiParameter(name='followee_id', description='奖励任务描述过滤'),]
    ),
    retrieve=extend_schema(summary='获取奖励任务详情',tags=['奖励任务管理']),
    create=extend_schema(summary='创建奖励任务',tags=['奖励任务管理']),
    update=extend_schema(summary='更新奖励任务',tags=['奖励任务管理']),
    partial_update=extend_schema(summary='部分更新奖励任务',tags=['奖励任务管理']),
    destroy=extend_schema(summary='删除奖励任务',tags=['奖励任务管理'])
)
class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = TaskRewardSerializer
    # def get(self,request, *args, **kwargs):
    #     ser = TaskRewardSerializer(instance=queryset, many=True)
    #
    #     return ApiResponse(ser)

@extend_schema_view(
    list=extend_schema(summary='获取任务模板列表（分页)',tags=['任务模板管理'],
        parameters=[OpenApiParameter(name='follower_id', description='任务模板类型过滤'),
        OpenApiParameter(name='followee_id', description='任务模板描述过滤'),]
    ),
    retrieve=extend_schema(summary='获取任务模板详情',tags=['任务模板管理']),
    create=extend_schema(summary='创建任务模板',tags=['任务模板管理']),
    update=extend_schema(summary='更新任务模板',tags=['任务模板管理']),
    partial_update=extend_schema(summary='部分更新任务模板',tags=['任务模板管理']),
    destroy=extend_schema(summary='删除任务模板',tags=['任务模板管理'])
)
class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TaskTemplateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        ser = TaskTemplateSerializer(instance=queryset, many=True)
        return ApiResponse(code=200, data=ser.data, message="任务模板列表获取成功")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = TaskTemplateSerializer(instance=instance)
        return ApiResponse(code=200, data=ser.data, message="任务模板详情获取成功")
