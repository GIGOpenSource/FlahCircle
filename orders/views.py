from rest_framework import viewsets

from middleware.base_views import BaseViewSet
from orders.models import Order
from orders.serializers import OrderSerializer


class OrderViewSet(BaseViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
