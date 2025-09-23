from django.db import models

# 用于首页短视频 / 发现页长视频表
class Content(models.Model):
    DYNAMIC_TYPES = (
        ('short', '短视频'),
        ('long', '长视频'),
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    data = models.CharField(max_length=255, blank=True, null=True)
    cover_url = models.JSONField(blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)
    author_id = models.IntegerField(blank=True, null=True)
    author_nickname = models.CharField(max_length=255, blank=True, null=True)
    author_avatar = models.CharField(max_length=255, blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    category_name = models.CharField(max_length=255, blank=True, null=True)
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

    class Meta:
        db_table = 't_content'
        ordering = ['create_time', 'title']


