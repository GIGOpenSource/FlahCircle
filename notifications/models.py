from django.db import models

class Notification(models.Model):
    app_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    send_time = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True, default=False)
    is_sent = models.BooleanField(blank=True, null=True, default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_notifications'
        ordering = ['create_time']