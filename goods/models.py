from django.db import models

class Good(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    original_price = models.IntegerField(blank=True, null=True)
    coin_price = models.IntegerField(blank=True, null=True)
    coin_amount = models.IntegerField(blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)
    cover_url = models.CharField(max_length=255, blank=True, null=True)
    images = models.JSONField(blank=True, null=True)
    sort = models.IntegerField(blank=True, null=True, default=0)
    is_online = models.BooleanField(blank=True, null=True, default=False)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_goods'
        ordering = ['create_time', 'title']
