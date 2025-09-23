from rest_framework import viewsets
from contents.models import Content
from contents.serializers import ContentSerializer
from middleware.base_views import BaseViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
@extend_schema_view(
    list=extend_schema(summary='获取短/长视频',tags=['短/长视频'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取短/长视频详情',tags=['短/长视频']),
    create=extend_schema(summary='创建短/长视频',tags=['短/长视频']),
    update=extend_schema(summary='更新短/长视频',tags=['短/长视频']),
    partial_update=extend_schema(summary='部分更新短/长视频',tags=['短/长视频']),
    destroy=extend_schema(summary='删除短/长视频',tags=['短/长视频'])
)
class ContentViewSet(BaseViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
