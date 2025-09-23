from rest_framework.decorators import action

from follows.models import Follow
from rest_framework import filters
from follows.serializers import FollowSerializer, FollowToggleSerializer
from middleware.base_views import BaseViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django_filters.rest_framework import DjangoFilterBackend

from middleware.utils import CustomPagination, ApiResponse


@extend_schema_view(
    list=extend_schema(summary='获取关注列表（分页)',tags=['关注管理'],
        parameters=[OpenApiParameter(name='follower_id', description='关注类型过滤'),
        OpenApiParameter(name='followee_id', description='关注描述过滤'),]
    ),
    retrieve=extend_schema(summary='获取关注详情',tags=['关注管理']),
    create=extend_schema(summary='创建关注',tags=['关注管理']),
    update=extend_schema(summary='更新关注',tags=['关注管理']),
    partial_update=extend_schema(summary='部分更新关注',tags=['关注管理']),
    destroy=extend_schema(summary='删除关注',tags=['关注管理'])
)
class FollowViewSet(BaseViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['follower_id', 'followee_id']
    search_fields = ['followee_nickname']

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

    @extend_schema(
        summary='关注/取消关注切换',
        tags=['关注管理'],
        request=FollowToggleSerializer,
        responses={200: FollowSerializer}
    )
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        关注/取消关注切换接口
        如果未关注则创建关注记录，如果已关注则取消关注
        """
        serializer = FollowToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        followee_id = serializer.validated_data['followee_id']
        follower_id = request.user.id

        # 不能关注自己
        if follower_id == followee_id:
            return ApiResponse(code=400, message="不能关注自己")

        # 验证被关注用户是否存在
        from user.models import User
        try:
            User.objects.get(id=followee_id)
        except User.DoesNotExist:
            return ApiResponse(code=400, message="被关注用户不存在")

        # 查找是否已存在关注记录
        follow, created = Follow.objects.get_or_create(
            follower_id=follower_id,
            followee_id=followee_id,
            defaults={
                'status': 'active'
            }
        )

        message = ""
        if not created:
            # 如果记录已存在，切换状态
            if follow.status == 'active':
                follow.status = 'inactive'
                message = "取消关注成功"
            else:
                follow.status = 'active'
                message = "关注成功"
            follow.save()
        else:
            message = "关注成功"

        # 返回更新后的关注信息
        result_serializer = FollowSerializer(follow)
        return ApiResponse(data=result_serializer.data, message=message)

    def perform_create(self, serializer):
        # 自动设置当前用户为关注者
        serializer.save(follower_id=self.request.user.id)

    def get_queryset(self):
        # 只返回当前用户的关注记录
        if self.request.user.is_authenticated:
            return Follow.objects.filter(follower_id=self.request.user.id)
        return Follow.objects.none()