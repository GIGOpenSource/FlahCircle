from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group

from chat.models import Session
from follows.models import Follow
from societies.models import Dynamic
from tags.models import Tag

User = get_user_model()

class GroupSerializer(serializers.ModelSerializer):
    """用户组序列化器"""
    class Meta:
        model = Group
        fields = ['id', 'name']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    groups = GroupSerializer(many=True, read_only=True)  # 只读展示用户组详情
    group_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Group.objects.all(),
        source='groups',
        required=False,
        help_text="用户组ID列表"
    )  # 用于修改用户所属组
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )
    is_follower = serializers.SerializerMethodField()
    session_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'user_nickname', 'email', 'phone', 'avatar','likes_count','following_count','followers_count',
            'member_level', 'user_bio', 'groups', 'group_ids', 'date_joined', 'session_id', 'is_follower','is_vip',
            'tags'
        ]
        read_only_fields = ['id', 'username', 'date_joined']

    def get_is_follower(self, obj):
        """
        获取当前登录用户是否关注了该用户
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # 检查当前登录用户(request.user)是否关注了该用户(obj)
            return Follow.objects.filter(
                follower_id=request.user.id,
                followee_id=obj.id,
                status='active'
            ).exists()
        return False

    def get_session_id(self, obj):
        """
        获取当前登录用户与该用户之间的会话ID
        如果存在会话则返回session_id，否则返回None
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.id != obj.id:
            try:
                from django.db.models import Q
                # 获取当前登录用户(request.user)与该用户(obj)之间的会话ID
                session = Session.objects.get(
                    Q(user_id=request.user.id, other_user_id=obj.id) |
                    Q(user_id=obj.id, other_user_id=request.user.id)
                )
                return session.session_id
            except Session.DoesNotExist:
                return None
        return None

    def to_representation(self, instance):
        """自定义序列化输出"""
        data = super().to_representation(instance)
        # 处理标签信息的序列化
        if instance.tags.exists():
            data['tags'] = [
                {
                    'id': tag.id,
                    'name': tag.name,
                    'description': tag.description,
                    'type': tag.type
                }
                for tag in instance.tags.all()
            ]
        else:
            data['tags'] = []
        return data

    def update(self, instance, validated_data):
        # 允许更新除 username 外的所有字段
        instance.user_nickname = validated_data.get('user_nickname', instance.user_nickname)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.member_level = validated_data.get('member_level', instance.member_level)
        instance.user_bio = validated_data.get('user_bio', instance.user_bio)
        instance.save()
        # 处理标签更新
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)

        instance.save()
        return instance



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)  # 确认密码字段
    user_nickname = serializers.CharField(required=False, allow_blank=True, max_length=50)
    username = serializers.CharField(required=True, max_length=150)  # 添加 username 为必填项

    class Meta:
        model = User
        fields = ('username', 'user_nickname', 'email', 'password', 'password2', 'phone')
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, data):
        """验证密码一致性"""
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError({"password2": "两次输入的密码不一致"})

        return data

    def validate_username(self, value):
        """验证 username 的唯一性"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被使用")
        return value

    def create(self, validated_data):
        # 如果提供了昵称则使用，否则在模型中自动生成
        validated_data.pop('password2', None)
        user_nickname = validated_data.pop('user_nickname', None)
        password = validated_data.pop('password')

        # 确保用户名不为空
        if not validated_data.get('username'):
            if validated_data.get('email'):
                validated_data['username'] = validated_data['email'].split('@')[0]
            else:
                from django.utils.crypto import get_random_string
                validated_data['username'] = f"user_{get_random_string(10, '0123456789abcdefghijklmnopqrstuvwxyz')}"

        user = User(**validated_data)
        if user_nickname:
            user.user_nickname = user_nickname
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """验证登录数据"""
        username = data.get('username')
        password = data.get('password')

        if not username:
            raise serializers.ValidationError("用户名不能为空")
        if not password:
            raise serializers.ValidationError("密码不能为空")

        return data
