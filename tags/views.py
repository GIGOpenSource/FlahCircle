from rest_framework import viewsets

from middleware.base_views import BaseViewSet
from tags.models import Tag
from tags.serializers import TagSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter


@extend_schema_view(
    list=extend_schema(summary='获取兴趣标签列表（分页)',tags=['兴趣标签管理'],
        parameters=[OpenApiParameter(name='follower_id', description='兴趣标签类型过滤'),
        OpenApiParameter(name='followee_id', description='兴趣标签描述过滤'),]
    ),
    retrieve=extend_schema(summary='获取兴趣标签详情',tags=['兴趣标签管理']),
    create=extend_schema(summary='创建兴趣标签',tags=['兴趣标签管理']),
    update=extend_schema(summary='更新兴趣标签',tags=['兴趣标签管理']),
    partial_update=extend_schema(summary='部分更新兴趣标签',tags=['兴趣标签管理']),
    destroy=extend_schema(summary='删除兴趣标签',tags=['兴趣标签管理'])
)
class TagViewSet(BaseViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer