import json

from rest_framework import serializers
from payments.models import Payment, Settings, Benefits


class BenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefits
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    benefits = serializers.PrimaryKeyRelatedField(
        queryset=Benefits.objects.all(),
        many=True,
        required=False
    )
    class Meta:
        model = Payment
        fields = '__all__'

    def create(self, validated_data):
        # 提取 benefits 数据
        benefits_data = validated_data.pop('benefits', [])
        # 创建 Payment 对象
        payment = Payment.objects.create(**validated_data)
        # 设置多对多关系
        if benefits_data:
            payment.benefits.set(benefits_data)
        return payment

    def update(self, instance, validated_data):
        # 提取 benefits 数据
        benefits_data = validated_data.pop('benefits', None)
        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if benefits_data is not None:
            instance.benefits.set(benefits_data)
        return instance

class PaymentSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = '__all__'