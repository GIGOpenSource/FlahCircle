from django.db import models

from contents.models import Content
from societies.models import Dynamic
from comments.models import Comment
from user.models import User

class Like(models.Model):
    LIKE_TYPES = (
        ('dynamic', '动态'),
        ('content', '内容'),
        ('comment', '评论'),
        ('video', '视频'),
    )

    STATUS_CHOICES = (
        ('active', '已点赞'),
        ('inactive', '已取消'),
    )

    type = models.CharField(max_length=20, choices=LIKE_TYPES, default='dynamic')
    target_id = models.IntegerField()
    user_id = models.IntegerField()
    user_nickname = models.CharField(max_length=255, blank=True, null=True)
    user_avatar = models.CharField(max_length=255, blank=True, null=True)
    target_author_id = models.IntegerField(blank=True, null=True)
    target_title = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_like'
        ordering = ['-create_time']
        unique_together = ('type', 'target_id', 'user_id')

    def save(self, *args, **kwargs):
        # 自动填充用户信息
        if self.user_id and not self.user_nickname:
            try:
                user = User.objects.get(id=self.user_id)
                self.user_nickname = user.user_nickname
                if isinstance(user.avatar, str):
                    self.user_avatar = user.avatar
                elif user.avatar:
                    self.user_avatar = user.avatar.url
                else:
                    self.user_avatar = None
                self.user_member_level = user.member_level
            except User.DoesNotExist:
                pass

        # 自动填充目标信息
        if self.type == 'dynamic' and self.target_id and not self.target_title:
            try:
                dynamic = Dynamic.objects.get(id=self.target_id)
                self.target_author_id = dynamic.user_id
                self.target_title = dynamic.title
            except Dynamic.DoesNotExist:
                pass
        elif self.type == 'content' and self.target_id and not self.target_title:
            try:
                content = Content.objects.get(id=self.target_id)
                self.target_author_id = content.author.id if content.author else None
                self.target_title = content.title
            except Content.DoesNotExist:
                pass
        elif self.type == 'comment' and self.target_id and not self.target_title:
            try:
                comment = Comment.objects.get(id=self.target_id)
                self.target_author_id = comment.user_id
                # 评论的标题可以是内容的前50个字符
                self.target_title = comment.content[:50] if comment.content else ''
            except Comment.DoesNotExist:
                pass

        # 检查是否是状态更新
        old_status = None
        if self.pk:  # 如果是更新操作
            try:
                old_instance = Like.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Like.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # 只有在状态发生变化时才更新目标对象的like_count
        if self.target_id and old_status != self.status:
            try:
                if self.type == 'dynamic':
                    target = Dynamic.objects.get(id=self.target_id)
                elif self.type == 'content':
                    target = Content.objects.get(id=self.target_id)
                elif self.type == 'comment':
                    target = Comment.objects.get(id=self.target_id)
                else:
                    return

                if self.status == 'active' and old_status != 'active':
                    # 点赞，增加计数
                    target.like_count = target.like_count + 1
                elif self.status == 'inactive' and old_status == 'active':
                    # 取消点赞，减少计数（但不低于0）
                    target.like_count = max(0, target.like_count - 1)
                target.save(update_fields=['like_count'])
            except (Dynamic.DoesNotExist, Content.DoesNotExist, Comment.DoesNotExist):
                pass
