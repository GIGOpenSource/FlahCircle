# user/serializers.py
from rest_framework import serializers
from payments.models import Payment, Settings


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'


class PaymentSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = '__all__'