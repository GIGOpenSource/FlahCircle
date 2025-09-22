from django.db import models

class Dynamic(models.Model):
    content = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    images = models.JSONField(blank=True, null=True)
    video_url = models.JSONField(blank=True, null=True)
    is_free = models.BooleanField(default=True)
    is_vip = models.BooleanField(default=True)
    price = models.IntegerField(default=0)
    user_id = models.IntegerField()
    user_nickname = models.CharField(max_length=255, blank=True, null=True)
    user_avatar = models.CharField(max_length=255, blank=True, null=True)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 't_social_dynamic'
        ordering = ['create_time']



