from django.db import models


class Advertisement(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    click_url = models.CharField(max_length=255, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    target_type = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True, default=False)
    sort_order = models.IntegerField(blank=True, null=True, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.00)
    is_vip = models.BooleanField(default=False)
    class Meta:
        db_table = 't_ad'
        ordering = ['create_time', 'name']
