import json

from django.db import models
from user.models import User


class Benefits(models.Model):
    """会员权益表"""
    name = models.CharField(max_length=255, verbose_name='权益名称')
    benefits_icon = models.TextField(blank=True, null=True, verbose_name='权益图标链接')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_benefits'
        ordering = ['id']

    def __str__(self):
        return self.name

class Payment(models.Model):
    PAY_TYPE = (
        ('vip', 'VIP购买'),
        ('gold', '金币购买'),
        ('content', '内容购买'),
        ('goods', '商品购买')
    )
    pay_name = models.CharField(max_length=255, blank=True, null=True,verbose_name='支付名称')
    amount = models.FloatField(blank=True, null=True, default=0, verbose_name='充值原价金额')
    pay_price = models.FloatField(blank=True, null=True, default=0, verbose_name='支付折扣金额')
    pay_channel = models.CharField(choices=PAY_TYPE, max_length=255, blank=True, null=True, verbose_name='支付渠道对应 vip gold')
    days_num = models.IntegerField(blank=True, null=True, default=0, verbose_name='充值天数')
    gold_coin = models.IntegerField(blank=True, null=True, default=0, verbose_name='金币数量')
    status = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True, default=False,verbose_name='是否启用')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    promotion_text = models.TextField(blank=True, null=True,verbose_name='促销文案')
    benefits = models.ManyToManyField(Benefits, related_name='payments', blank=True, verbose_name='会员权益')
    class Meta:
        db_table = 't_payment'
        ordering = ['create_time']

class Settings(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    api_id = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    base_url = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_payment_settings'
        ordering = ['create_time']
