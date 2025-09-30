# user/serializers.py
from rest_framework import serializers
from orders.models import Order
from payments.models import Settings, Payment


class OrderSerializer(serializers.ModelSerializer):

    payment_info = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_payment_info(self, obj):
        """
        获取订单关联的支付信息（来自t_payment表）
        """
        try:
            # 根据订单的支付方法和金额查找匹配的支付配置
            payment = Payment.objects.filter(
                # pay_channel=obj.pay_method,  # 匹配支付类型(vip/gold等)
                # amount=obj.cash_amount,  # 匹配金额
                is_active=True,  # 只查找启用的支付配置
                status='true'  # 状态为启用
            ).first()

            if payment:
                return {
                    'id': payment.id,
                    'pay_name': payment.pay_name,
                    'amount': payment.amount,
                    'pay_price': payment.pay_price,
                    'pay_channel': payment.pay_channel,
                    'days_num': payment.days_num,
                    'gold_coin': payment.gold_coin,
                    'promotion_text': payment.promotion_text,
                    'is_active': payment.is_active
                }
            return None
        except Payment.DoesNotExist:
            return None
        except Exception:
            return None