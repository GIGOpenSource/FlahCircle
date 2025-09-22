from django.db import models

class Order(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    user_nickname = models.CharField(max_length=255, blank=True, null=True)
    goods_id = models.IntegerField(blank=True, null=True)
    goods_name = models.CharField(max_length=255, blank=True, null=True)
    goods_type = models.CharField(max_length=255, blank=True, null=True)
    goods_cover = models.CharField(max_length=255, blank=True, null=True)
    goods_category_name = models.CharField(max_length=255, blank=True, null=True)
    coin_amount = models.IntegerField(blank=True, null=True)
    content_id = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, default=1)
    payment_mode = models.CharField(max_length=255, blank=True, null=True)
    cash_amount = models.IntegerField(blank=True, null=True)
    coin_cost = models.IntegerField(blank=True, null=True)
    total_amount = models.IntegerField(blank=True, null=True)
    discount_amount = models.IntegerField(blank=True, null=True)
    final_amount = models.IntegerField(blank=True, null=True)
    pay_status = models.CharField(max_length=255, blank=True, null=True)
    pay_method = models.CharField(max_length=255, blank=True, null=True)
    pay_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_order'
        ordering = ['create_time']
