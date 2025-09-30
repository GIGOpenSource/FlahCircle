from django.db import models

from goods.models import Good
from payments.models import Payment
from user.models import User


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_user')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='order_payment')
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='order_good', blank=True, null=True)
    quantity = models.IntegerField(blank=True, default=1)
    cash_amount = models.IntegerField(blank=True, null=True)
    final_amount = models.IntegerField(blank=True, null=True)
    pay_status = models.CharField(max_length=255, blank=True, null=True)
    pay_method = models.CharField(max_length=255, blank=True, null=True)
    pay_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    # 新增字段用于支付接口
    trade_no = models.CharField(max_length=255, blank=True, null=True)  # 商户订单号
    merc_id = models.CharField(max_length=255, blank=True, null=True)  # 商户编号
    device_id = models.CharField(max_length=255, blank=True, null=True)  # 设备ID
    player_ip = models.CharField(max_length=255, blank=True, null=True)  # 玩家IP
    device_type = models.CharField(max_length=255, blank=True, null=True)  # 设备类型
    player_name = models.CharField(max_length=255, blank=True, null=True)  # 玩家姓名
    player_tel = models.CharField(max_length=255, blank=True, null=True)  # 玩家电话
    pay_account = models.CharField(max_length=255, blank=True, null=True)  # 付款账号
    notify_url = models.CharField(max_length=255, blank=True, null=True)  # 回调地址
    pay_money = models.IntegerField(blank=True, null=True)  # 实际支付金额
    notify_status = models.CharField(max_length=255, blank=True, null=True)  # 回调状态
    oid = models.CharField(max_length=255, blank=True, null=True)  # 支付平台订单号
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_order'
        ordering = ['create_time']
