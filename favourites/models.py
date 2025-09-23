from django.db import models

from societies.models import Dynamic
from user.models import User


class Favorite(models.Model):
    STATUS_CHOICES = (
        ('active', '已收藏'),
        ('inactive', '已取消'),
    )
    type = models.CharField(max_length=255, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    user_id =  models.IntegerField(blank=True, null=True)
    user_nickname = models.CharField(blank=True, null=True)
    target_title = models.CharField(max_length=255, blank=True, null=True)
    target_cover = models.CharField(max_length=255, blank=True, null=True)
    target_author_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_favorite'
        ordering = ['create_time']

    def save(self, *args, **kwargs):
        # 自动填充用户信息
        if self.user_id and not self.user_nickname:
            try:
                user = User.objects.get(id=self.user_id)
                self.user_nickname = user.user_nickname
            except User.DoesNotExist:
                pass

        # 检查是否是状态更新
        old_status = None
        if self.pk:  # 如果是更新操作
            try:
                old_instance = Favorite.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Favorite.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # 只要target_id存在，就更新Dynamic的favorite_count（不管type是什么）
        if self.target_id and old_status != self.status:
            try:
                dynamic = Dynamic.objects.get(id=self.target_id)
                if self.status == 'active' and old_status != 'active':
                    # 收藏，增加计数
                    dynamic.favorite_count = dynamic.favorite_count + 1
                elif self.status == 'inactive' and old_status == 'active':
                    # 取消收藏，减少计数（但不低于0）
                    dynamic.favorite_count = max(0, dynamic.favorite_count - 1)
                dynamic.save(update_fields=['favorite_count'])
            except Dynamic.DoesNotExist:
                pass

    def delete(self, *args, **kwargs):
        # 删除收藏时减少Dynamic的favorite_count
        if self.target_id and self.status == 'active':
            try:
                dynamic = Dynamic.objects.get(id=self.target_id)
                dynamic.favorite_count = max(0, dynamic.favorite_count - 1)
                dynamic.save(update_fields=['favorite_count'])
            except Dynamic.DoesNotExist:
                pass

        super().delete(*args, **kwargs)