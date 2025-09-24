from django.db import models

from user.models import User


class Message(models.Model):
    MESSAGE_TYPES = (
        ('text', '文本'),
        ('image', '图片'),
        ('video', '视频'),
        ('audio', '音频'),
        ('file', '文件'),
        ('system', '系统消息'),
    )
    sender_id = models.IntegerField(blank=True, null=True)
    receiver_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="房间号ID")
    content = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, choices=MESSAGE_TYPES, default='text')
    extra_data = models.JSONField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    reply_to_id = models.IntegerField(blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_message'
        ordering = ['create_time']

    def save(self, *args, **kwargs):
        # 自动填充发送者信息
        if self.sender_id and not hasattr(self, '_sender_info_set'):
            try:
                user = User.objects.get(id=self.sender_id)
                if not hasattr(self, '_sender_info_set'):
                    self._sender_info_set = True
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class Session(models.Model):
    SESSION_TYPES = (
        ('private', '私聊'),
        ('group', '群聊'),
    )
    user_id = models.IntegerField(blank=True, null=True, verbose_name="用户id")
    other_user_id = models.IntegerField(blank=True, null=True)
    session_id = models.CharField(max_length=255, unique=True, verbose_name="会话id")
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='private')
    last_message_id = models.IntegerField(blank=True, null=True)
    last_message_time = models.DateTimeField(blank=True, null=True)
    unread_count = models.IntegerField(blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_message_session'
        ordering = ['-update_time']
        unique_together = ('user_id', 'session_id')


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