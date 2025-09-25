from django.db import models
from user.models import User

class Reward(models.Model):
    STATUS_CHOICES = (
        ('pending', '待领取'),
        ('claimed', '已领取'),
        ('completed', '已完成'),
        ('expired', '已过期'),
    )
    task_template = models.ForeignKey('Template', on_delete=models.CASCADE, related_name='rewards', null=True,
                                      blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards', null=True, blank=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.IntegerField(default=0)
    data = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='pending')
    claimed_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_task_reward'
        ordering = ['create_time']


class Template(models.Model):
    TASK_TYPES = (
        ('daily', '每日任务'),
        ('checkin', '签到任务'),
        ('novice', '新手任务'),
    )

    type = models.CharField(max_length=255, choices=TASK_TYPES, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    action = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.IntegerField(default=0)
    data = models.JSONField(blank=True, null=True)
    sort = models.IntegerField(default=0)
    image_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="任务图片URL")
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_task_template'
        ordering = ['create_time']
