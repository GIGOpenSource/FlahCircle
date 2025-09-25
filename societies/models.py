import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

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
    price = models.IntegerField(default=0)
    user_id = models.IntegerField()
    user_nickname = models.CharField(max_length=255, blank=True, null=True)
    user_avatar = models.CharField(max_length=255, blank=True, null=True)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = 't_social_dynamic'
        ordering = ['-create_time']

    def save(self, *args, **kwargs):
        if not self.prefixed_id:
            self.prefixed_id = f"d_{uuid.uuid4().hex}"
        if self.user_id:
            try:
                user = User.objects.get(id=self.user_id)
                self.user_nickname = user.user_nickname
                if user.avatar:
                    self.user_avatar = user.avatar.url
                else:
                    self.user_avatar = None
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)

