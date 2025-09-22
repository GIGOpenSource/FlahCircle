from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)
    icon_url = models.CharField(max_length=255, blank=True, null=True)
    parent_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True, default=False)
    sort = models.IntegerField(blank=True, null=True, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_category'
        ordering = ['create_time', 'name']
