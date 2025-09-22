from django.db import models

class Follow(models.Model):
    follower_id = models.IntegerField(blank=True, null=True)
    followee_id = models.IntegerField(blank=True, null=True)
    follower_nickname = models.CharField(max_length=255, blank=True, null=True)
    follower_avatar = models.CharField(max_length=255, blank=True, null=True)
    followee_nickname = models.CharField(max_length=255, blank=True, null=True)
    followee_avatar = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_follow'
        ordering = ['create_time']