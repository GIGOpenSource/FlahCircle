from django.db import models
from user.models import User
from contents.models import Content


class Rating(models.Model):
    """
    评分模型
    用于记录用户对内容的评分历史
    """
    SCORE_CHOICES = (
        (1.0, '1分'),
        (1.5, '1.5分'),
        (2.0, '2分'),
        (2.5, '2.5分'),
        (3.0, '3分'),
        (3.5, '3.5分'),
        (4.0, '4分'),
        (4.5, '4.5分'),
        (5.0, '5分'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='ratings')
    score = models.FloatField(choices=SCORE_CHOICES)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_rating'
        ordering = ['-create_time']
        # 确保同一用户不能对同一内容重复评分
        unique_together = ('user', 'content')

    def save(self, *args, **kwargs):
        # 检查是否是更新操作
        old_score = None
        if self.pk:
            try:
                old_rating = Rating.objects.get(pk=self.pk)
                old_score = old_rating.score
            except Rating.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # 更新内容的评分统计
        try:
            content = Content.objects.get(id=self.content.id)
            if old_score is None:
                # 新评分，增加计数和总分
                content.score_total += self.score
                content.score_count += 1
            else:
                # 更新评分，调整总分
                content.score_total = content.score_total - old_score + self.score
            content.save(update_fields=['score_total', 'score_count'])
        except Content.DoesNotExist:
            pass

    def delete(self, *args, **kwargs):
        # 删除评分时减少内容的评分统计
        try:
            content = Content.objects.get(id=self.content.id)
            content.score_total -= self.score
            content.score_count = max(0, content.score_count - 1)
            content.save(update_fields=['score_total', 'score_count'])
        except Content.DoesNotExist:
            pass

        super().delete(*args, **kwargs)
