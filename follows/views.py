from follows.models import Follow
from rest_framework import filters
from follows.serializers import FollowSerializer
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