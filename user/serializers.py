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
    """用户信息序列化器（支持完整CRUD）"""
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
            'id', 'username', 'email', 'phone', 'avatar',
            'member_level', 'groups', 'group_ids', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']

# class GroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = ['id', 'name']
#         read_only_fields = ['id']

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "两次密码不一致"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)