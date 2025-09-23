from rest_framework import viewsets
from contents.models import Content
from contents.serializers import ContentSerializer
from middleware.base_views import BaseViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
@extend_schema_view(
    list=extend_schema(summary='获取文章内容',tags=['文章内容'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取文章内容详情',tags=['文章内容']),
    create=extend_schema(summary='创建文章内容',tags=['文章内容']),
    update=extend_schema(summary='更新文章内容',tags=['文章内容']),
    partial_update=extend_schema(summary='部分更新文章内容',tags=['文章内容']),
    destroy=extend_schema(summary='删除文章内容',tags=['文章内容'])
)
class ContentViewSet(BaseViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
