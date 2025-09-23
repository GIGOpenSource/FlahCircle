from django.db import models

from societies.models import Dynamic
from user.models import User


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

    def save(self, *args, **kwargs):
        # 检查是否是新建评论
        is_new = self.pk is None

        # 自动填充用户信息
        if self.user_id and (not self.user_nickname or not self.user_avatar):
            try:
                user = User.objects.get(id=self.user_id)
                self.user_nickname = user.user_nickname
                self.user_avatar = user.avatar.url if user.avatar else None
            except User.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # 如果是新建评论且target_id存在，增加Dynamic的comment_count
        if is_new and self.target_id:
            try:
                dynamic = Dynamic.objects.get(id=self.target_id)
                dynamic.comment_count = dynamic.comment_count + 1
                dynamic.save(update_fields=['comment_count'])
            except Dynamic.DoesNotExist:
                pass

    def delete(self, *args, **kwargs):
        # 如果target_id存在，减少Dynamic的comment_count
        if self.target_id:
            try:
                dynamic = Dynamic.objects.get(id=self.target_id)
                dynamic.comment_count = max(0, dynamic.comment_count - 1)
                dynamic.save(update_fields=['comment_count'])
            except Dynamic.DoesNotExist:
                pass

        super().delete(*args, **kwargs)