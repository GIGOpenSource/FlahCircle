import hashlib
import hmac
import json
import urllib.parse
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema
from middleware.base_views import BaseViewSet
from payments.models import Payment, Settings
from payments.serializers import PaymentSerializer, PaymentSettingsSerializer


@extend_schema_view(
    list=extend_schema(summary='支付权限列表', tags=['权限']),
    retrieve=extend_schema(summary='支付权限详情', tags=['权限'])
)
class PaymentViewSet(BaseViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'], url_path='initiate')
    def initiate_payment(self, request):
        """
        发起支付 - 前端调用此接口获取支付网关地址
        """
        # 获取用户信息（通过Token）
        user = request.user
        device_id = request.data.get('device_id', 'default_device_id')  # 模拟设备ID

        # 获取支付参数
        amount = request.data.get('amount')
        pay_method = request.data.get('pay_method', 'default')

        # 获取支付配置
        settings = Settings.objects.first()
        if not settings:
            return Response({'error': '支付配置不存在'}, status=400)

        # 创建订单记录
        payment = Payment.objects.create(
            user_id=user.id,
            user_nickname=user.nickname if hasattr(user, 'nickname') else user.username,
            amount=amount,
            pay_method=pay_method,
            api_id=settings.api_id,
            api_key=settings.api_key,
            base_url=settings.base_url,
            status='pending'
        )

        # 构造支付网关URL参数
        params = {
            'api_id': settings.api_id,
            'amount': amount,
            'order_id': payment.id,  # 使用payment的ID作为订单ID
            'device_id': device_id,
            # 可以根据需要添加其他参数
        }

        # 构造完整支付网关URL
        query_string = urllib.parse.urlencode(params)
        payment_gateway_url = f"{settings.base_url}?{query_string}"

        # 更新支付记录
        payment.order_id = payment.id
        payment.save()

        return Response({
            'payment_gateway_url': payment_gateway_url,
            'order_id': payment.id
        })


@extend_schema_view(
    list=extend_schema(summary='支付设置列表', tags=['权限']),
    retrieve=extend_schema(summary='支付设置详情', tags=['权限'])
)
class PaymentSettingsViewSet(BaseViewSet):
    queryset = Settings.objects.all()
    serializer_class = PaymentSettingsSerializer


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    """
    支付回调视图 - 处理支付网关的回调通知
    """

    def post(self, request):
        # 获取回调数据
        callback_data = request.POST.dict()

        # 获取订单ID
        order_id = callback_data.get('order_id')
        if not order_id:
            return HttpResponse('Missing order_id', status=400)

        try:
            # 查找对应的支付记录
            payment = Payment.objects.get(id=order_id)
        except Payment.DoesNotExist:
            return HttpResponse('Payment not found', status=404)

        # 验证签名
        if not self.verify_signature(callback_data, payment.api_key):
            return HttpResponse('Invalid signature', status=400)

        # 更新支付状态
        status = callback_data.get('status')
        if status:
            payment.status = status
            payment.update_time = timezone.now()
            payment.save()

        # 可以在这里添加其他业务逻辑，如通知用户、更新账户余额等

        # 返回成功响应
        return HttpResponse('success')

    def verify_signature(self, data, api_key):
        """
        验证回调签名
        这里假设签名是基于所有参数和api_key的HMAC-SHA256哈希
        根据实际支付网关的签名规则进行调整
        """
        # 提取签名
        signature = data.pop('sign', '')
        if not signature:
            return False

        # 按键排序参数
        sorted_data = sorted(data.items())
        # 构造待签名字符串
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_data])
        # 添加API密钥
        sign_string = f"{query_string}&key={api_key}"
        # 计算签名
        expected_signature = hmac.new(
            api_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # 比较签名
        return signature == expected_signature
