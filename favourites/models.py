from django.db import models

class Favorite(models.Model):
    type = models.CharField(max_length=255, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    user_id =  models.IntegerField(blank=True, null=True)
    user_nickname = models.IntegerField(blank=True, null=True)
    target_title = models.CharField(max_length=255, blank=True, null=True)
    target_cover = models.CharField(max_length=255, blank=True, null=True)
    target_author_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_favorite'
        ordering = ['create_time']

