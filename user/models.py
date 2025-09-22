# user/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    """扩展内置用户模型，增加会员等级"""
    MEMBER_LEVEL = (
        ('normal', '普通用户'),
        ('vip', 'VIP用户'),
        ('svip', 'SVIP用户'),
    )
    phone = models.CharField(max_length=11, blank=True, null=True, unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    member_level = models.CharField(max_length=10, choices=MEMBER_LEVEL, default='normal')
    # 保留Django内置的groups和user_permissions用于分组权限
    groups = models.ManyToManyField(
        Group,
        related_name='custom_users',  # 避免内置User的groups冲突
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users',
        blank=True,
    )

    class Meta:
        db_table = 'custom_user'

    def is_creator(self):
        """判断用户是否为创作者"""
        return self.groups.filter(name='Creator').exists()

    def is_admin_role(self):
        """判断用户是否为管理员"""
        return self.groups.filter(name='Admin').exists()