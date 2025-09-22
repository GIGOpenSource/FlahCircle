from django.db import models

class Reward(models.Model):
    task_template_id = models.IntegerField()
    type = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.IntegerField(default=0)
    data = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_task_reward'
        ordering = ['create_time']


class Template(models.Model):
    task_id = models.IntegerField()
    type = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    action = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.IntegerField(default=0)
    data = models.JSONField(blank=True, null=True)
    sort = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_task_template'
        ordering = ['create_time']
