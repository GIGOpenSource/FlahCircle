from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from goods.models import Good
from goods.serializers import GoodSerializer
from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse, CustomPagination
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

@extend_schema_view(
    list=extend_schema(summary='获取物品列表',tags=['物品管理'],
        parameters=[OpenApiParameter(name='type', description='物品类型过滤'),
        OpenApiParameter(name='description', description='物品描述过滤'),]
    ),
    retrieve=extend_schema(summary='获取物品详情',tags=['物品管理']),
    create=extend_schema(summary='创建物品',tags=['物品管理']),
    update=extend_schema(summary='更新物品',tags=['物品管理']),
    partial_update=extend_schema(summary='部分更新物品',tags=['物品管理']),
    destroy=extend_schema(summary='删除物品',tags=['物品管理'])
)
class GoodViewSet(BaseViewSet):
    queryset = Good.objects.all()
    serializer_class = GoodSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'description']
    search_fields = ['name', 'title', 'description']
    ordering = ['-create_time']
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