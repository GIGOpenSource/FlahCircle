from django.db import models

class Message(models.Model):
    sender_id = models.IntegerField(blank=True, null=True)
    receiver_id = models.IntegerField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    extra_data = models.JSONField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    reply_to_id = models.IntegerField(blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_message'
        ordering = ['create_time']


class Session(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    other_user_id = models.IntegerField(blank=True, null=True)
    last_message_id = models.IntegerField(blank=True, null=True)
    last_message_time = models.DateTimeField(blank=True, null=True)
    unread_count = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_message_session'
        ordering = ['create_time']


class Settings(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    allow_stranger_msg = models.BooleanField(default=False)
    auto_read_receipt = models.BooleanField(default=False)
    message_notification = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_message_setting'
        ordering = ['create_time']