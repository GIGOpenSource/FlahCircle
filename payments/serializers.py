import json

from rest_framework import serializers
from payments.models import Payment, Settings, Benefits


class BenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefits
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    benefits = BenefitsSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class PaymentSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = '__all__'