from django.db import models

from societies.models import Dynamic
from user.models import User


class Follow(models.Model):
    STATUS_CHOICES = (
        ('active', '已关注'),
        ('inactive', '已取消'),
    )
    follower_id = models.IntegerField(blank=True, null=True,verbose_name="自己")
    followee_id = models.IntegerField(blank=True, null=True,verbose_name="关注了谁")
    follower_nickname = models.CharField(max_length=255, blank=True, null=True)
    follower_avatar = models.CharField(max_length=255, blank=True, null=True)
    followee_nickname = models.CharField(max_length=255, blank=True, null=True)
    followee_avatar = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_follow'
        ordering = ['create_time']

    def save(self, *args, **kwargs):
        # 自动填充用户信息
        if self.follower_id and not self.follower_nickname:
            try:
                follower = User.objects.get(id=self.follower_id)
                self.follower_nickname = follower.user_nickname
                self.follower_avatar = follower.avatar.url if follower.avatar else None
            except User.DoesNotExist:
                pass

        if self.followee_id and not self.followee_nickname:
            try:
                followee = User.objects.get(id=self.followee_id)
                self.followee_nickname = followee.user_nickname
                self.followee_avatar = followee.avatar.url if followee.avatar else None
            except User.DoesNotExist:
                pass

        # 检查是否是状态更新
        old_status = None
        if self.pk:  # 如果是更新操作
            try:
                old_instance = Follow.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Follow.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # 更新用户模型中的关注计数字段
        if old_status != self.status:
            try:
                # 更新关注者的关注数量
                follower_user = User.objects.get(id=self.follower_id)
                # 更新被关注者的粉丝数量
                followee_user = User.objects.get(id=self.followee_id)

                if self.status == 'active' and old_status != 'active':
                    # 关注，增加计数
                    follower_user.following_count = follower_user.following_count + 1
                    followee_user.followers_count = followee_user.followers_count + 1
                elif self.status == 'inactive' and old_status == 'active':
                    # 取消关注，减少计数（但不低于0）
                    follower_user.following_count = max(0, follower_user.following_count - 1)
                    followee_user.followers_count = max(0, followee_user.followers_count - 1)

                follower_user.save(update_fields=['following_count'])
                followee_user.save(update_fields=['followers_count'])
            except User.DoesNotExist:
                pass

    def delete(self, *args, **kwargs):
        # 删除关注时减少计数
        if self.status == 'active':
            try:
                follower_user = User.objects.get(id=self.follower_id)
                followee_user = User.objects.get(id=self.followee_id)
                follower_user.following_count = max(0, follower_user.following_count - 1)
                followee_user.followers_count = max(0, followee_user.followers_count - 1)
                follower_user.save(update_fields=['following_count'])
                followee_user.save(update_fields=['followers_count'])
            except User.DoesNotExist:
                pass

        super().delete(*args, **kwargs)