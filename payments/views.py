from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets

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

@extend_schema_view(
    list=extend_schema(summary='支付设置列表', tags=['权限']),
    retrieve=extend_schema(summary='支付设置详情', tags=['权限'])
)
class PaymentSettingsViewSet(BaseViewSet):
    queryset = Settings.objects.all()
    serializer_class = PaymentSettingsSerializer