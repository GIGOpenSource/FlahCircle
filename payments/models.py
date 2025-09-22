from django.db import models

class Payment(models.Model):
    order_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    user_nickname = models.CharField(max_length=255, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True, default=0)
    pay_method = models.CharField(max_length=255, blank=True, null=True)
    pay_channel = models.CharField(max_length=255, blank=True, null=True)
    api_id = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    base_url = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_payment'
        ordering = ['create_time']


class Settings(models.Model):
    api_id = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    base_url = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_payment_settings'
        ordering = ['create_time']