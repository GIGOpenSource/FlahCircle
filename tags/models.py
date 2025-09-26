from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    usage_count = models.IntegerField(default=0)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_tag'
        ordering = ['create_time']

    def get_related_users(self):
        """
        获取关联此标签的用户，按关注者数量排序
        """
        return self.users.filter(is_active=True).order_by('-followers_count')