from django.db import models

from societies.models import Dynamic
from contents.models import Content
from user.models import User


class Favorite(models.Model):
    STATUS_CHOICES = (
        ('active', '已收藏'),
        ('inactive', '已取消'),
    )
    TYPE_CHOICES = (
        ('dynamic', '动态'),
        ('content', '内容'),
    )
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, blank=True, null=True)
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

        # 只要target_id存在，就更新目标对象的favorite_count
        if self.target_id and old_status != self.status:
            try:
                if self.type == 'dynamic':
                    target = Dynamic.objects.get(id=self.target_id)
                elif self.type == 'content':
                    target = Content.objects.get(id=self.target_id)
                else:
                    return

                if self.status == 'active' and old_status != 'active':
                    # 收藏，增加计数
                    target.favorite_count = target.favorite_count + 1
                elif self.status == 'inactive' and old_status == 'active':
                    # 取消收藏，减少计数（但不低于0）
                    target.favorite_count = max(0, target.favorite_count - 1)
                target.save(update_fields=['favorite_count'])
            except (Dynamic.DoesNotExist, Content.DoesNotExist):
                pass

    def delete(self, *args, **kwargs):
        # 删除收藏时减少目标对象的favorite_count
        if self.target_id and self.status == 'active':
            try:
                if self.type == 'dynamic':
                    target = Dynamic.objects.get(id=self.target_id)
                elif self.type == 'content':
                    target = Content.objects.get(id=self.target_id)
                else:
                    return

                target.favorite_count = max(0, target.favorite_count - 1)
                target.save(update_fields=['favorite_count'])
            except (Dynamic.DoesNotExist, Content.DoesNotExist):
                pass

        super().delete(*args, **kwargs)


class Downvote(models.Model):
    """
    点踩（踩）模型
    用于记录用户对内容的负面评价
    """
    STATUS_CHOICES = (
        ('active', '已点踩'),
        ('inactive', '已取消'),
    )
    TYPE_CHOICES = (
        ('dynamic', '动态'),
        ('content', '内容'),
    )

    type = models.CharField(max_length=255, choices=TYPE_CHOICES, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    user_nickname = models.CharField(blank=True, null=True)
    target_title = models.CharField(max_length=255, blank=True, null=True)
    target_cover = models.CharField(max_length=255, blank=True, null=True)
    target_author_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_downvote'
        ordering = ['create_time']
        # 确保同一用户不能对同一目标重复点踩
        unique_together = ('type', 'target_id', 'user_id')

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
                old_instance = Downvote.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Downvote.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # 只要target_id存在，就更新目标对象的downvote_total
        if self.target_id and old_status != self.status:
            try:
                # 根据类型更新相应对象的downvote_total字段
                if self.type == 'dynamic':
                    target = Dynamic.objects.get(id=self.target_id)
                elif self.type == 'content':
                    target = Content.objects.get(id=self.target_id)
                else:
                    return

                if self.status == 'active' and old_status != 'active':
                    # 点踩，增加计数
                    target.downvote_total = target.downvote_total + 1
                elif self.status == 'inactive' and old_status == 'active':
                    # 取消点踩，减少计数（但不低于0）
                    target.downvote_total = max(0, target.downvote_total - 1)
                target.save(update_fields=['downvote_total'])
            except (Dynamic.DoesNotExist, Content.DoesNotExist):
                pass

    def delete(self, *args, **kwargs):
        # 删除点踩记录时减少目标对象的downvote_total
        if self.target_id and self.status == 'active':
            try:
                if self.type == 'dynamic':
                    target = Dynamic.objects.get(id=self.target_id)
                elif self.type == 'content':
                    target = Content.objects.get(id=self.target_id)
                else:
                    return

                target.downvote_total = max(0, target.downvote_total - 1)
                target.save(update_fields=['downvote_total'])
            except (Dynamic.DoesNotExist, Content.DoesNotExist):
                pass

        super().delete(*args, **kwargs)
