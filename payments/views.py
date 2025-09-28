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
from middleware.utils import CustomPagination
from payments.models import Payment, Settings, Benefits
from payments.serializers import PaymentSerializer, PaymentSettingsSerializer, BenefitsSerializer
from orders.models import Order


@extend_schema(tags=["支付模板管理"])
@extend_schema_view(
    list=extend_schema(summary='支付模板列表',
    parameters=[OpenApiParameter(name='pay_channel', description='支付类型过滤'),]),
    retrieve=extend_schema(summary='支付详情')
)
class PaymentViewSet(BaseViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pay_channel']

@extend_schema(tags=["支付管理"])
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

@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    """
    支付回调视图 - 处理支付网关的回调通知
    """

    def post(self, request):
        # 获取回调数据
        trade_no = request.POST.get('tradeNo') or request.GET.get('tradeNo')
        pay_status = request.POST.get('payStatus') or request.GET.get('payStatus', '已支付')
        pay_time = request.POST.get('payTime') or request.GET.get('payTime')
        pay_money = request.POST.get('payMoney') or request.GET.get('payMoney')
        notify_status = request.POST.get('notifyStatus') or request.GET.get('notifyStatus', '回调成功')

        if not trade_no:
            return HttpResponse('Missing tradeNo', status=400)

        try:
            # 查找对应的支付记录
            payment = Payment.objects.get(order_id=trade_no)
        except Payment.DoesNotExist:
            return HttpResponse('Payment not found', status=404)

        # 更新支付状态
        payment.status = pay_status
        payment.update_time = timezone.now()
        payment.save()

        # 同时更新订单状态
        try:
            order = Order.objects.get(trade_no=trade_no)
            order.pay_status = pay_status
            order.notify_status = notify_status

            if pay_time:
                # 解析支付时间
                try:
                    order.pay_time = timezone.datetime.fromisoformat(pay_time.replace('Z', '+00:00'))
                except Exception:
                    pass

            if pay_money:
                try:
                    order.pay_money = int(float(pay_money))
                except Exception:
                    pass

            order.update_time = timezone.now()
            order.save()
        except Order.DoesNotExist:
            pass

        # 返回成功响应
        return HttpResponse('success')
