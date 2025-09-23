from rest_framework import viewsets
from categories.models import Category
from categories.serializers import CategorySerializer
from middleware.base_views import BaseViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
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
