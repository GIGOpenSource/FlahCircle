from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import filters

from middleware.base_views import BaseViewSet
from middleware.utils import CustomPagination, ApiResponse
from societies.models import Dynamic
from societies.serializers import SocialDynamicSerializer

@extend_schema_view(
    list=extend_schema(summary='获取动态视频',tags=['社区动态'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取动态视频详情',tags=['社区动态']),
    create=extend_schema(summary='创建动态视频',tags=['社区动态']),
    update=extend_schema(summary='更新动态视频',tags=['社区动态']),
    partial_update=extend_schema(summary='部分更新动态视频',tags=['社区动态']),
    destroy=extend_schema(summary='删除动态视频',tags=['社区动态'])
)
class DynamicViewSet(BaseViewSet):
    queryset = Dynamic.objects.all()
    serializer_class = SocialDynamicSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['type']

    def list(self, request, *args, **kwargs):
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