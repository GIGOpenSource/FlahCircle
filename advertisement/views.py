from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from advertisement.models import Advertisement
from advertisement.serializers import AdvertisementSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from middleware.base_views import BaseViewSet


@extend_schema_view(
    list=extend_schema(
        summary='获取广告列表',
        description='支持按类型(type)过滤、搜索(q)、排序和分页',
        tags=['广告管理'],
        parameters=[
            OpenApiParameter(name='type', description='广告类型过滤'),
            OpenApiParameter(name='q', description='搜索关键词(名称/标题)'),
            OpenApiParameter(name='ordering', description='排序字段(如:sort_order,-create_time)'),
        ]
    ),
    retrieve=extend_schema(
        summary='获取广告详情',
        description='根据ID获取单个广告的详细信息',
        tags=['广告管理']
    ),
    create=extend_schema(
        summary='创建广告',
        description='新增一条广告记录',
        tags=['广告管理']
    ),
    update=extend_schema(
        summary='更新广告',
        description='全量更新广告信息',
        tags=['广告管理']
    ),
    partial_update=extend_schema(
        summary='部分更新广告',
        description='部分字段更新广告信息',
        tags=['广告管理']
    ),
    destroy=extend_schema(
        summary='删除广告',
        description='根据ID删除指定广告',
        tags=['广告管理']
    )
)
class AdvertisementViewSet(BaseViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_active']  # 支持按类型和状态过滤
    search_fields = ['name', 'title', 'description']  # 支持搜索的字段
    ordering_fields = ['create_time', 'update_time', 'sort_order']  # 支持排序的字段
    ordering = ['-create_time']  # 默认排序
