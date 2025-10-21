from datetime import datetime

from advertisement.models import Advertisement
from advertisement.serializers import AdvertisementSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from middleware.base_views import BaseViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from middleware.utils import CustomPagination
from middleware.utils import ApiResponse
from user.models import UserPurchase


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

    from rest_framework.decorators import action
    from django.db import transaction

    @action(detail=True, methods=['post'], url_path='adv_purchase')
    @transaction.atomic
    def perform_video(self, request, pk=None):
        """
       购买视频访问权限
       参数:
       - id: 视频ID
       """
        try:
            # 获取视频对象
            advertise = Advertisement.objects.get(pk=pk, is_vip=True)  # 假设is_vip字段标识VIP视频
        except advertise.DoesNotExist:
            return ApiResponse(code=404, message="广告不存在")
        user = request.user
        if user.gold_coin < advertise.price:
            return ApiResponse(code=400, message="金币不足,无法购买")
        try:
            user.gold_coin -= advertise.price
            user.save(update_fields=['gold_coin'])
            userPurchase = UserPurchase.objects.create()
            userPurchase.content_type = "advertise"
            userPurchase.user = user
            userPurchase.object_id = pk
            userPurchase.purchase_time = datetime.now()
            userPurchase.price = advertise.price
            userPurchase.save()
        except Exception as e:
            print(repr(e))
            return ApiResponse(code=500, message="购买失败")
        return ApiResponse(message="购买成功", data={'remaining_coins': user.gold_coin})