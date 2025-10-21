import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

import categories
from user.models import User


class Dynamic(models.Model):
    DYNAMIC_TYPES = (
        ('video', '视频'),
        ('dynamic', '动态'),
    )
    TABS_CHOICES = (
        ('follow', '关注'),
        ('latest', '最新'),
        ('recommend', '推荐'),
        ('cashback', '发现'),
        ('selected', '精选'),
    )
    # 前缀的ID字段
    prefixed_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    tabs = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=TABS_CHOICES
    )
    type = models.CharField(max_length=255, choices=DYNAMIC_TYPES,blank=True, null=True)
    images = models.JSONField(blank=True, null=True, help_text="图片URL数组，例如: ['url1', 'url2']")
    video_url = models.JSONField(blank=True, null=True)
    is_free = models.BooleanField(default=True)
    is_vip = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,verbose_name="价格")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dynamics')
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(blank=True, null=True, default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="纬度")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="经度")
    categories = models.ManyToManyField('categories.Category', related_name='dynamics', blank=True, verbose_name="标签")
    class Meta:
        db_table = 't_social_dynamic'
        ordering = ['-create_time']

    def save(self, *args, **kwargs):
        if not self.prefixed_id:
            self.prefixed_id = f"d_{uuid.uuid4().hex}"
        super().save(*args, **kwargs)

