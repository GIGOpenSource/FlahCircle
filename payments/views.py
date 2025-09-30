import hashlib
import hmac
import json
import urllib.parse
import uuid
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from middleware.base_views import BaseViewSet
from middleware.utils import CustomPagination, ApiResponse
from payments.models import Payment, Settings, Benefits
from payments.serializers import PaymentSerializer, PaymentSettingsSerializer, BenefitsSerializer
from orders.models import Order


@extend_schema(tags=["支付模板管理"])
@extend_schema_view(
    list=extend_schema(summary='支付模板列表',
    parameters=[OpenApiParameter(name='pay_channel', description='支付类型过滤'),
                OpenApiParameter(name='is_active', description='上线下线过滤'),
                ]),
    retrieve=extend_schema(summary='支付详情')
)
class PaymentViewSet(BaseViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pay_channel','is_active']

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



@extend_schema(tags=["支付API管理"])
@extend_schema_view(
    list=extend_schema(summary='支付设置列表'),
    retrieve=extend_schema(summary='支付设置详情')
)
class PaymentSettingsViewSet(BaseViewSet):
    queryset = Settings.objects.all()
    serializer_class = PaymentSettingsSerializer


@extend_schema(tags=["会员权益管理"])
@extend_schema_view(
    list=extend_schema(summary='会员权益列表'),
    retrieve=extend_schema(summary='会员权益详情'),
    create=extend_schema(summary='创建会员权益'),
    update=extend_schema(summary='更新会员权益'),
    partial_update=extend_schema(summary='部分更新会员权益'),
    destroy=extend_schema(summary='删除会员权益')
)
class BenefitsViewSet(BaseViewSet):
    queryset = Benefits.objects.all()
    serializer_class = BenefitsSerializer
    pagination_class = CustomPagination
