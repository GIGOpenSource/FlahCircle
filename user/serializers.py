# user/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group

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

    class Meta:
        model = User
        fields = [
            'id', 'username', 'user_nickname', 'email', 'phone', 'avatar',
            'member_level', 'user_bio', 'groups', 'group_ids', 'date_joined'
        ]
        read_only_fields = ['id', 'username', 'date_joined']

    def update(self, instance, validated_data):
        # 允许更新除 username 外的所有字段
        instance.user_nickname = validated_data.get('user_nickname', instance.user_nickname)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.member_level = validated_data.get('member_level', instance.member_level)
        instance.user_bio = validated_data.get('user_bio', instance.user_bio)
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