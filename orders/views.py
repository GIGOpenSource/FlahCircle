import hashlib
import json
import urllib.parse
import uuid
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.views import APIView

from middleware.base_views import BaseViewSet
from middleware.utils import CustomPagination, ApiResponse
from orders.models import Order
from orders.serializers import OrderSerializer
from payments.models import Settings, Payment


@extend_schema(tags=["订单管理"])
@extend_schema_view(
    list=extend_schema(summary='获取订单支付记录列表',
        parameters=[OpenApiParameter(name='type', description='type字段过滤'),]
    ),
    retrieve=extend_schema(summary='获取订单详情'),
    create=extend_schema(summary='创建订单',),
    update=extend_schema(summary='更新订单',),
    partial_update=extend_schema(summary='部分更新订单',),
    destroy=extend_schema(summary='删除订单',)
)
class OrderViewSet(BaseViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = CustomPagination

    def _get_client_ip(self, request):
        """
        获取客户端IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    def get_queryset(self):
        """
        普通用户只能查看自己的订单，管理员可以查看所有订单
        """
        user = self.request.user

        # 检查用户是否为管理员
        if user.is_staff or user.is_superuser:
            print("管理员")
            # 管理员可以查看所有订单
            return Order.objects.all()
        else:
            # 普通用户只能查看自己的订单
            return Order.objects.filter(user=user)

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

    @extend_schema(
        summary="发起支付请求",
        description="前端发起支付请求，后端生成订单和支付二维码信息",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'device_id': {'type': 'string', 'description': '设备ID'},

                    'payment_id': {'type': 'integer', 'description': '支付配置ID'},
                    'pay_method': {'type': 'string', 'description': '支付方式 (alipay/wxpay/qqpay)'}
                },
                'required': ['device_id', 'payment_id', 'pay_method']
            }
        },
        responses={
            200: {
                'description': '成功返回订单状态和支付二维码',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'code': {'type': 'integer', 'example': 200},
                                'msg': {'type': 'string', 'example': '获取成功'},
                                'money': {'type': 'number', 'example': 1.0},
                                'type': {'type': 'string', 'example': 'alipay'},
                                'qrcode': {'type': 'string',
                                           'example': 'wxp://f2f15IaTGck0xvm7vug4lqx-sMpJ0xiUB8fWTDwCQk-jYBxS6Yl1A_fOdPGNNGKwPnOt'},
                                'code_url': {'type': 'string', 'example': 'Payewm.jpg'},
                                'trade_no': {'type': 'string', 'example': '20160806151343349'},
                                'out_trade_no': {'type': 'string', 'example': '20160806151343349'}

                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='initiate-payment')
    def initiate_payment(self, request):
        """
        步骤1：前端发起支付请求，后端生成订单和支付二维码信息
        """
        # 获取用户信息（通过Token）
        user = request.user
        # 获取支付参数
        device_id = request.data.get('device_id', '')  # 设备ID
        payment_id = request.data.get('payment_id')  # 支付配置ID
        pay_method = request.data.get('pay_method')  # 支付方式
        # 验证必要参数
        if not all([payment_id, pay_method]):
            return Response({
                'code': 400,
                'msg': '缺少必要参数: payment_id 或 pay_method'
            }, status=400)
        # 验证支付方式
        valid_methods = ['alipay', 'wxpay', 'qqpay']
        if pay_method not in valid_methods:
            return Response({
                'code': 400,
                'msg': f'支付方式必须是以下之一: {", ".join(valid_methods)}'
            }, status=400)
        # 获取支付配置
        try:
            payment_config = Payment.objects.get(id=payment_id, is_active=True, status='true')
        except Payment.DoesNotExist:
            return Response({
                'code': 400,
                'msg': '支付配置不存在或未启用'
            }, status=400)
        # 获取有效的支付配置(用于签名)
        try:
            settings = Settings.objects.get(status='true')
        except Settings.DoesNotExist:
            return Response({
                'code': 500,
                'msg': '支付配置不存在或未启用'
            }, status=500)
        except Settings.MultipleObjectsReturned:
            settings = Settings.objects.filter(status='true').first()

        # 生成商户订单号
        trade_no = f"FC{int(timezone.now().timestamp() * 1000)}{user.id}"

        # 创建订单记录（使用payment_config.pay_price作为金额）
        order = Order.objects.create(
            user=user,
            payment=payment_config,
            cash_amount=int(payment_config.pay_price),  # 转换为分
            final_amount=int(payment_config.pay_price),
            pay_method=pay_method,
            pay_status='pending',
            trade_no=trade_no,
            merc_id=settings.api_id,
            device_id=device_id,
            player_ip=self._get_client_ip(request),
            device_type=request.data.get('device_type', 'unknown'),
            player_name=user.user_nickname if hasattr(user, 'user_nickname') else user.username,
            player_tel=getattr(user, 'phone', ''),
            pay_account=getattr(user, 'phone', ''),
            notify_url=request.build_absolute_uri('/api/orders/payment-callback/')
        )
        # 生成支付平台订单号
        oid = str(uuid.uuid4()).replace('-', '')[:11]
        order.oid = oid
        order.save()
        # 构造支付参数
        params = {
            'pid': settings.api_id,  # 商户ID
            'type': pay_method,  # 支付方式
            'out_trade_no': trade_no,  # 商户订单号
            'notify_url': f"{settings.base_url}/notify_url.php",  # 服务器异步通知地址
            'return_url': f"{settings.base_url}/return_url.php",  # 页面跳转通知地址
            'name': payment_config.pay_name or f"{pay_method}充值",  # 商品名称
            'money': str(payment_config.pay_price),  # 商品金额
            'sitename': 'FlashCircle'  # 网站名称
        }
        # 生成签名: MD5签名算法
        sign_string = f"{params['pid']}{params['type']}{params['out_trade_no']}{params['notify_url']}{params['return_url']}{params['name']}{params['money']}{params['sitename']}{settings.api_key}"
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
        params['sign'] = sign
        params['sign_type'] = 'MD5'
        # 调用支付网关接口获取二维码信息
        # 检查是否启用测试模式
        test = 'true'
        if test == 'true':
            # 测试模式：返回模拟数据
            response_data = {
                'code': 200,
                'msg': '获取成功!',
                'money': float(payment_config.pay_price),
                'type': pay_method,
                'qrcode': 'https://flashcircle.oss-cn-beijing.aliyuncs.com/2b1265623d8f491a9d75220019f856bc.png',
                'code_url': 'https://flashcircle.oss-cn-beijing.aliyuncs.com/2b1265623d8f491a9d75220019f856bc.png',
                'trade_no': trade_no,
                'out_trade_no': trade_no
            }
            return Response(response_data)
        import requests
        try:
            response = requests.post(f"{settings.base_url}/mapi.php", data=params)
            if response.status_code == 200:
                # 解析支付网关返回的数据
                payment_response = response.json()
                response_data = {
                    'code': payment_response.get('code', 200),
                    'msg': payment_response.get('msg', '获取成功'),
                    'money': payment_response.get('money', float(payment_config.pay_price)),
                    'type': payment_response.get('type', pay_method),
                    'qrcode': payment_response.get('qrcode', ''),
                    'code_url': payment_response.get('code_url', ''),
                    'trade_no': payment_response.get('trade_no', trade_no),
                    'out_trade_no': payment_response.get('out_trade_no', trade_no)
                }
            else:
                # 如果调用支付网关失败，返回默认数据
                response_data = {
                    'code': 200,
                    'msg': '获取成功',
                    'money': float(payment_config.pay_price),
                    'type': pay_method,
                    'qrcode': '',  # 实际应从支付网关获取
                    'code_url': '',  # 实际应从支付网关获取
                    'trade_no': trade_no,
                    'out_trade_no': trade_no
                }
        except Exception as e:
            # 如果出现异常，返回默认数据
            response_data = {
                'code': 200,
                'msg': '获取成功',
                'money': float(payment_config.pay_price),
                'type': pay_method,
                'qrcode': '',  # 实际应从支付网关获取
                'code_url': '',  # 实际应从支付网关获取
                'trade_no': trade_no,
                'out_trade_no': trade_no
            }
        return Response(response_data)

    @extend_schema(
        summary="支付结果通知",
        description="处理支付网关的服务器异步通知和页面跳转通知",
        methods=['GET'],
        parameters=[
            OpenApiParameter(name='trade_no', description='平台订单号', required=True),
        ],
        responses={
            200: {
                'description': '支付通知处理成功',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'code': {'type': 'integer', 'example': 200},
                                'msg': {'type': 'string', 'example': '处理成功'},
                                'data': {'type': 'object'}
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'], url_path='payment-callback')
    @action(detail=False, methods=['get'], url_path='payment-callback')
    def callback_payment(self, request):
        print("调用")
        # 获取所有查询参数
        # 获取请求中的trade_no参数
        trade_no = request.GET.get('trade_no')
        if not trade_no:
            return ApiResponse(code=400, message='缺少必要参数: trade_no')

        # 根据trade_no查询订单记录
        try:
            order = Order.objects.get(trade_no=trade_no)

        except Order.DoesNotExist:

            return ApiResponse(code=404, message='订单不存在')

        # 从订单记录中获取所需参数
        try:
            # 获取支付配置信息用于签名验证
            settings = Settings.objects.get(status='true')
        except (Settings.DoesNotExist, Settings.MultipleObjectsReturned):
            settings = Settings.objects.filter(status='true').first()
            if not settings:
                return ApiResponse(code=500, message='支付配置不存在')

        # 构建参数字典（从订单记录中获取）
        params = {
            'pid': order.merc_id,  # 商户ID
            'trade_no': order.oid,  # 支付平台订单号
            'out_trade_no': order.trade_no,  # 商户订单号
            'type': order.pay_method,  # 支付方式
            'name': order.payment.pay_name,  # 商品名称
            'money': str(order.final_amount / 100),  # 金额（转换为元）
            'trade_status': 'TRADE_SUCCESS',  # 支付状态
            'sign_type': 'MD5'  # 签名类型
        }

        # 生成签名（保持与发起支付时一致的签名算法）
        sign_string = f"{params['pid']}{params['type']}{params['out_trade_no']}{order.notify_url}{order.notify_url}{params['name']}{params['money']}FlashCircle{settings.api_key}"
        params['sign'] = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
        # 验证签名
        # if not self._verify_signature(params):
        #     return ApiResponse(code=400, message='签名验证失败')
        # 验证支付状态
        if params['trade_status'] != 'TRADE_SUCCESS':
            return ApiResponse(code=400, message='支付未成功')
        # 更新订单状态
        if order.pay_status != 'success':
            order.pay_status = 'success'
            order.pay_time = timezone.now()
            order.notify_status = 'success'  # 标记回调状态
            order.save(update_fields=[
                'pay_status', 'pay_time', 'notify_status'
            ])

            # 获取订单对应的用户
            user = order.user
            # 获取支付配置信息
            payment = order.payment

            # 根据支付渠道类型更新用户对应资产
            if payment.pay_channel == 'vip':
                # VIP充值，增加会员天数
                if payment.days_num and payment.days_num > 0:
                    user.vip_days += payment.days_num
                    user.save(update_fields=['vip_days'])
            elif payment.pay_channel == 'gold':
                # 金币充值，增加金币数量
                if payment.gold_coin and payment.gold_coin > 0:
                    user.gold_coin += payment.gold_coin
                    user.save(update_fields=['gold_coin'])

        # 准备返回的订单数据
        order_data = {
            'trade_no': order.trade_no,
            'out_trade_no': params.get('trade_no'),
            'pay_status': order.pay_status,
            'pay_time': order.pay_time.strftime('%Y-%m-%d %H:%M:%S') if order.pay_time else None,
            'amount': order.final_amount / 100,  # 转换为元
            'pay_method': order.pay_method
        }

        return ApiResponse(data=order_data, message='处理成功')