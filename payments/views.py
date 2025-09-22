from rest_framework import viewsets
from payments.models import Payment, Settings
from payments.serializers import PaymentSerializer, PaymentSettingsSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentSettingsViewSet(viewsets.ModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = PaymentSettingsSerializer