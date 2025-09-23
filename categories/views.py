from rest_framework import viewsets
from categories.models import Category
from categories.serializers import CategorySerializer
from middleware.base_views import BaseViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from middleware.utils import ApiResponse, CustomPagination


@extend_schema_view(
    list=extend_schema(summary='获取发现-精选',tags=['发现-精选'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取发现-精选详情',tags=['发现-精选']),
    create=extend_schema(summary='创建发现-精选',tags=['发现-精选']),
    update=extend_schema(summary='更新发现-精选',tags=['发现-精选']),
    partial_update=extend_schema(summary='部分更新发现-精选',tags=['发现-精选']),
    destroy=extend_schema(summary='删除发现-精选',tags=['发现-精选'])
)
class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination
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