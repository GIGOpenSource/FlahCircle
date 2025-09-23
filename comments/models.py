from django.db import models

class Comment(models.Model):
    type = models.CharField(max_length=255, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    parent_comment_id = models.IntegerField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    user_nickname = models.CharField(max_length=255, blank=True, null=True)
    user_avatar = models.CharField(max_length=255, blank=True, null=True)
    reply_to_user_id = models.IntegerField(blank=True, null=True)
    reply_to_user_nickname = models.CharField(max_length=255, blank=True, null=True)
    reply_to_user_avatar = models.CharField(max_length=255, blank=True, null=True)
    like_count = models.IntegerField(blank=True, null=True, default=0)
    reply_count = models.IntegerField(blank=True, null=True, default=0)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_comment'
        ordering = ['create_time']
