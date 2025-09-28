import hashlib
import json
import urllib.parse
import uuid
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from middleware.base_views import BaseViewSet
from middleware.utils import CustomPagination, ApiResponse
from orders.models import Order
from orders.serializers import OrderSerializer
from payments.models import Settings


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

    def get_queryset(self):
        """
        普通用户只能查看自己的订单，管理员可以查看所有订单
        """
        user = self.request.user

        # 检查用户是否为管理员
        if user.is_staff or user.is_superuser:
            # 管理员可以查看所有订单
            return Order.objects.all()
        else:
            # 普通用户只能查看自己的订单
            return Order.objects.filter(user=user)
        return queryset

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
        description="前端发起支付请求，后端生成签名、订单号，返回支付URL",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'device_id': {'type': 'string', 'description': '设备ID'},
                    'type': {'type': 'string', 'description': '支付类型 (vip/gold)', 'default': 'gold'},
                    'money': {'type': 'integer', 'description': '支付金额'}
                },
                'required': ['device_id', 'type', 'money']
            }
        },
        responses={
            200: {
                'description': '成功返回订单状态',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'code': {'type': 'integer', 'example': 200},
                                'msg': {
                                    'type': 'object',
                                    'properties': {
                                        'oid': {'type': 'string', 'example': 'o2NkR3btS0i'},
                                        'payUrl': {'type': 'string', 'example': 'https://**/**'},
                                        'sign': {'type': 'string', 'example': 'df006fe7a5d2e911a826opa2ab459773'},
                                        'mode': {'type': 'string', 'example': 'url'}
                                    }
                                }
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
        步骤1：前端发起支付请求，后端生成签名、订单号，返回支付URL
        """
        # 获取用户信息（通过Token）
        user = request.user

        # 获取支付参数
        device_id = request.data.get('device_id', '')  # 设备ID
        pay_type = request.data.get('type', 'gold')  # 支付类型 (vip/gold)
        money = request.data.get('money', 0)  # 支付金额

        # 获取有效的支付配置
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

        # 创建订单记录
        order = Order.objects.create(
            user=user,
            cash_amount=int(money),
            final_amount=int(money),
            pay_method=pay_type,
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
            'mercId': settings.api_id,      # 商户编号
            'type': pay_type,               # 订单充值类型
            'money': str(money),            # 充值额
            'tradeNo': trade_no,            # 商户订单号
            'notifyUrl': request.build_absolute_uri('/api/orders/payment-callback/'),  # 回调地址
        }

        # 添加玩家信息
        player_info = {
            'playerId': str(user.id),       # 玩家ID
            'playerIp': self._get_client_ip(request),  # 玩家IP
            'deviceId': device_id,          # 玩家设备ID
            'deviceType': request.data.get('device_type', 'unknown'),  # 玩家设备类型
            'name': user.user_nickname if hasattr(user, 'user_nickname') else user.username,  # 玩家姓名
            'tel': getattr(user, 'phone', ''),  # 玩家手机号
            'payAct': getattr(user, 'phone', ''),  # 玩家付款账号
        }

        # 时间戳
        timestamp = str(int(timezone.now().timestamp() * 1000))  # UTC时间戳(13位)

        # 生成签名: md5(mercId + money + notifyUrl + tradeNo + type + appSecret)
        sign_string = f"{params['mercId']}{params['money']}{params['notifyUrl']}{params['tradeNo']}{params['type']}{settings.api_key}"
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()

        # 构造完整支付网关URL
        query_params = []
        for key, value in params.items():
            query_params.append(f"{key}={urllib.parse.quote(str(value))}")

        # 单独处理info参数
        query_params.append(f"info={urllib.parse.quote(json.dumps(player_info))}")
        query_params.append(f"time={timestamp}")
        query_params.append(f"mode=sdk")
        query_params.append(f"sign={sign}")

        query_string = "&".join(query_params)
        payment_gateway_url = f"{settings.base_url}?{query_string}"
        payment_gateway_url = "https://flashcircle.oss-cn-beijing.aliyuncs.com/001.png"

        # 返回响应
        return Response({
            'code': 200,
            'msg': {
                'oid': oid,                 # 支付平台订单号
                'payUrl': payment_gateway_url,  # 支付链接
                'sign': sign,               # 签名
                'mode': 'url'               # 支付模式
            }
        })

    @extend_schema(
        summary="校验订单状态",
        description="支付完成后校验订单状态",
        parameters=[
            OpenApiParameter(name='tradeNo', description='商户订单号', required=True, type=str)
        ],
        responses={
            200: {
                'description': '成功返回订单状态',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'code': {'type': 'integer', 'example': 200},
                                'msg': {
                                    'type': 'object',
                                    'properties': {
                                        'mercId': {'type': 'string', 'example': '10001'},
                                        'tradeNo': {'type': 'string', 'example': 'U20181031144202170R4'},
                                        'money': {'type': 'string', 'example': '5000'},
                                        'payMoney': {'type': 'string', 'example': '5000'},
                                        'payTime': {'type': 'string', 'example': '2018-11-08T11:20:49.000Z'},
                                        'payStatus': {'type': 'string', 'example': '已付'},
                                        'notifyStatus': {'type': 'string', 'example': '回调成功'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'], url_path='query-order')
    def query_order(self, request):
        """
        步骤2：查询订单状态
        """
        trade_no = request.query_params.get('tradeNo')

        if not trade_no:
            return Response({
                'code': 400,
                'msg': '缺少订单号参数'
            }, status=400)

        try:
            order = Order.objects.get(trade_no=trade_no)
        except Order.DoesNotExist:
            return Response({
                'code': 404,
                'msg': '订单不存在'
            }, status=404)

        # 返回订单状态信息
        return Response({
            'code': 200,
            'msg': {
                'mercId': order.merc_id,
                'tradeNo': order.trade_no,
                'money': str(order.cash_amount),
                'payMoney': str(order.pay_money or order.cash_amount),
                'payTime': order.pay_time.isoformat() if order.pay_time else None,
                'payStatus': order.pay_status,
                'notifyStatus': order.notify_status or '未回调'
            }
        })

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

    @extend_schema(
        summary="订单状态查询",
        description="按照支付网关指定格式查询订单状态",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'mercId': {'type': 'string', 'description': '商户编号'},
                    'tradeNo': {'type': 'string', 'description': '商户订单号'}
                },
                'required': ['mercId', 'tradeNo']
            }
        },
        responses={
            200: {
                'description': '成功返回订单状态',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'code': {'type': 'integer', 'example': 200},
                                'msg': {
                                    'type': 'object',
                                    'properties': {
                                        'mercId': {'type': 'string', 'example': '10001'},
                                        'tradeNo': {'type': 'string', 'example': 'U20181031144202170R4'},
                                        'money': {'type': 'string', 'example': '5000'},
                                        'payMoney': {'type': 'string', 'example': '5000'},
                                        'payTime': {'type': 'string', 'example': '2018-11-08T11:20:49.000Z'},
                                        'payStatus': {'type': 'string', 'example': '已付'},
                                        'notifyStatus': {'type': 'string', 'example': '回调成功'}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': '查询失败',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'code': {'type': 'integer', 'example': 400},
                                'err': {'type': 'string', 'example': '查询失败'}
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='query-order-status')
    def query_order_status(self, request):
        """
        订单状态查询接口
        实现 ${gateway}/api/shark/order/queryOrder 接口
        """
        # 获取请求参数
        merc_id = request.data.get('mercId')
        trade_no = request.data.get('tradeNo')

        # 验证必要参数
        if not merc_id or not trade_no:
            return Response({
                'code': 400,
                'err': '查询失败'
            }, status=400)

        try:
            # 查找订单
            order = Order.objects.get(merc_id=merc_id, trade_no=trade_no)
        except Order.DoesNotExist:
            return Response({
                'code': 400,
                'err': '查询失败'
            }, status=400)

        # 按照指定格式返回订单状态信息
        response_data = {
            'code': 200,
            'msg': {
                'mercId': order.merc_id,
                'tradeNo': order.trade_no,
                'money': str(order.cash_amount),
                'payMoney': str(order.pay_money or order.cash_amount),
                'payTime': order.pay_time.isoformat() if order.pay_time else None,
                'payStatus': order.pay_status or '未支付',
                'notifyStatus': order.notify_status or '未回调'
            }
        }
        return Response(response_data)

@method_decorator(csrf_exempt, name='dispatch')
class OrderPaymentCallbackView(View):
    """
    订单支付回调视图 - 处理支付网关的回调通知
    用户付款成功后，支付网关会向notifyUrl发送通知
    服务器只需返回"success"表示回调已收到
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
            # 查找对应的订单记录
            order = Order.objects.get(trade_no=trade_no)
        except Order.DoesNotExist:
            return HttpResponse('Order not found', status=404)

        # 更新订单状态
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
        # 返回成功响应，支付网关收到"success"表示回调已收到
        return HttpResponse('success')