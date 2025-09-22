# user/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.crypto import get_random_string


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
    bio = models.TextField(blank=True, null=True, verbose_name="个人简介")  # 新增个人简介
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name="昵称", unique=True)
    # username 可更改且必填
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名")
    # 关注和粉丝数量可以通过关系计算，但为了性能考虑可以添加缓存字段
    followers_count = models.PositiveIntegerField(default=0, verbose_name="粉丝数量")
    following_count = models.PositiveIntegerField(default=0, verbose_name="关注数量")
    likes_count = models.PositiveIntegerField(default=0, verbose_name="获赞数量")

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

    USERNAME_FIELD = 'username'  # 使用 username 作为登录字段
    REQUIRED_FIELDS = ['email']  # 创建超级用户时需要的字段

    class Meta:
        db_table = 'custom_user'

    def save(self, *args, **kwargs):
        # 如果是新建用户且没有 nickname，则自动生成
        if not self.nickname:
            # 生成自增的 nickname
            last_user = User.objects.order_by('-id').first()
            if last_user and last_user.nickname and last_user.nickname.startswith('user_'):
                try:
                    last_number = int(last_user.nickname.split('_')[1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    next_number = 1
            else:
                next_number = 1

            self.nickname = f"user_{next_number:06d}"  # 格式如 user_000001

            # 确保 nickname 唯一性（以防万一）
            while User.objects.filter(nickname=self.nickname).exists():
                next_number += 1
                self.nickname = f"user_{next_number:06d}"

        super().save(*args, **kwargs)

    def is_creator(self):
        """判断用户是否为创作者"""
        return self.groups.filter(name='Creator').exists()

    def is_admin_role(self):
        """判断用户是否为管理员"""
        return self.member_level == "admin"
        # return self.groups.filter(name='Admin').exists()

    def get_followers_count(self):
        """获取粉丝数量（实时计算）"""
        from follows.models import Follow  # 避免循环导入
        return Follow.objects.filter(following=self, is_active=True).count()

    def get_following_count(self):
        """获取关注数量（实时计算）"""
        from follows.models import Follow  # 避免循环导入
        return Follow.objects.filter(follower=self, is_active=True).count()

    def get_likes_count(self):
        """获取获赞数量（实时计算）"""
        from likes.models import Like  # 避免循环导入
        # 假设点赞是针对用户创建的内容，如帖子、商品等
        # 这里需要根据你的具体业务逻辑调整
        return Like.objects.filter(target_user=self, is_active=True).count()

    def is_followed_by(self, user):
        """判断当前用户是否被指定用户关注"""
        if not user.is_authenticated:
            return False
        from follows.models import Follow  # 避免循环导入
        return Follow.objects.filter(
            follower=user,
            following=self,
            is_active=True
        ).exists()
