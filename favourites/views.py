from rest_framework import viewsets
from favourites.models import Favorite
from favourites.serializers import FavoriteSerializer
from middleware.base_views import BaseViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

@extend_schema_view(
    list=extend_schema(summary='获取收藏',tags=['收藏管理'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取收藏详情',tags=['收藏管理']),
    create=extend_schema(summary='创建收藏',tags=['收藏管理']),
    update=extend_schema(summary='更新收藏',tags=['收藏管理']),
    partial_update=extend_schema(summary='部分更新收藏',tags=['收藏管理']),
    destroy=extend_schema(summary='删除收藏',tags=['收藏管理'])
)
class FavoriteViewSet(BaseViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
