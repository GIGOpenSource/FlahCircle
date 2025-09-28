# user/serializers.py
import json

from rest_framework import serializers
from payments.models import Payment, Settings


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'

    def get_membership_benefits(self, obj):
        """获取会员权益，返回数组格式"""
        if obj.membership_benefits:
            try:
                return json.loads(obj.membership_benefits)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def to_representation(self, instance):
        """序列化输出时的处理"""
        data = super().to_representation(instance)
        data['membership_benefits'] = self.get_membership_benefits(instance)
        return data

    def to_internal_value(self, data):
        """反序列化输入时的处理"""
        # 复制数据以避免修改原始数据
        mutable_data = data.copy()

        # 如果传入的是列表，转换为JSON字符串存储
        if 'membership_benefits' in mutable_data and isinstance(mutable_data['membership_benefits'], list):
            mutable_data['membership_benefits'] = json.dumps(mutable_data['membership_benefits'], ensure_ascii=False)
        elif 'membership_benefits' in mutable_data and isinstance(mutable_data['membership_benefits'], str):
            # 如果已经是字符串，尝试验证是否为有效的JSON
            try:
                json.loads(mutable_data['membership_benefits'])
            except (json.JSONDecodeError, TypeError):
                # 如果不是有效的JSON，包装成数组格式
                mutable_data['membership_benefits'] = json.dumps([mutable_data['membership_benefits']],
                                                                 ensure_ascii=False)

        return super().to_internal_value(mutable_data)


class PaymentSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = '__all__'