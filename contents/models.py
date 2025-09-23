from django.db import models
from user.models import User

# 用于首页短视频 / 发现页长视频表
class Content(models.Model):
    DYNAMIC_TYPES = (
        ('short', '短视频'),
        ('long', '长视频'),
    )
    TABS_CHOICES = (
        ('follow', '关注'),
        ('latest', '最新'),
        ('recommend', '推荐'),
        ('cashback', '发现'),
        ('selected', '精选'),
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, choices=DYNAMIC_TYPES, blank=True, null=True)
    data = models.CharField(max_length=255, blank=True, null=True)
    cover_url = models.JSONField(blank=True, null=True)
    tabs = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=TABS_CHOICES
    )
    author_id = models.IntegerField(blank=True, null=True)
    author_nickname = models.CharField(max_length=255, blank=True, null=True)
    author_avatar = models.CharField(max_length=255, blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True, verbose_name="标签id")
    category_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="标签name")
    status = models.CharField(max_length=255, blank=True, null=True)
    review_status = models.CharField(max_length=255, blank=True, null=True)
    view_count = models.IntegerField(blank=True, null=True, default=0)
    like_count = models.IntegerField(blank=True, null=True, default=0)
    comment_count = models.IntegerField(blank=True, null=True, default=0)
    favorite_count = models.IntegerField(blank=True, null=True, default=0)
    share_count = models.IntegerField(blank=True, null=True, default=0)
    score_count = models.IntegerField(blank=True, null=True, default=0)
    score_total = models.IntegerField(blank=True, null=True, default=0)
    publish_time = models.DateTimeField(blank=True, null=True)
    is_vip = models.BooleanField(default=False)
    is_permanent = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    object_fit = models.CharField(max_length=255, blank=True, null=True)
    fullScreenShow = models.BooleanField(default=True)
    class Meta:
        db_table = 't_content'
        ordering = ['-create_time']  # 修改为按创建时间倒序

    def save(self, *args, **kwargs):
        # 修复字段名错误
        if self.author_id:
            try:
                user = User.objects.get(id=self.author_id)
                self.author_nickname = user.user_nickname
                if user.avatar:
                    self.author_avatar = user.avatar.url if user.avatar else None
                else:
                    self.author_avatar = None
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)
