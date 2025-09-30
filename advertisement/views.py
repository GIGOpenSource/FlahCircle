from advertisement.models import Advertisement
from advertisement.serializers import AdvertisementSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from middleware.base_views import BaseViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from middleware.utils import CustomPagination
from middleware.utils import ApiResponse

@extend_schema(tags=["广告管理"])
@extend_schema_view(
    list=extend_schema(summary='获取广告列表',
        parameters=[OpenApiParameter(name='type', description='广告类型过滤'),]
    ),
    retrieve=extend_schema(summary='获取广告详情'),
    create=extend_schema(summary='创建广告'),
    update=extend_schema(summary='更新广告'),
    partial_update=extend_schema(summary='部分更新广告'),
    destroy=extend_schema(summary='删除广告')
)
class AdvertisementViewSet(BaseViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_active']
    search_fields = ['name', 'title', 'description']
    ordering_fields = ['create_time', 'update_time', 'sort_order']
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