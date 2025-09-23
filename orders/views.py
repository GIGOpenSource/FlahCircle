from rest_framework import viewsets

from middleware.base_views import BaseViewSet
from orders.models import Order
from orders.serializers import OrderSerializer

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter


@extend_schema_view(
    list=extend_schema(summary='获取排序配置',tags=['排序'],
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取排序配置详情',tags=['排序']),
    create=extend_schema(summary='创建排序配置',tags=['排序']),
    update=extend_schema(summary='更新排序配置',tags=['排序']),
    partial_update=extend_schema(summary='部分更新排序配置',tags=['排序']),
    destroy=extend_schema(summary='删除排序配置',tags=['排序'])
)
class OrderViewSet(BaseViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
