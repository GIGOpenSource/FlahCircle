from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, generics, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from datetime import timedelta

from middleware.base_views import BaseViewSet
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, GroupSerializer
from rest_framework.authtoken.models import Token
from middleware.utils import ApiResponse

User = get_user_model()

# @extend_schema(tags=["用户管理"])
@extend_schema(
    tags=["用户管理"],
    summary="用户注册",
    description="用户自主注册账号，返回认证token",
    request=UserRegisterSerializer,
    responses={201: "注册成功", 400: "参数错误"}
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return ApiResponse(data={
                'user_id': user.id,
                'username': user.username,
                'user_nickname': user.user_nickname,
                'token': token.key
            })
        return ApiResponse(code=400, message=serializer.errors)


@extend_schema(tags=["用户管理"])
class CustomLoginView(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id="user-login",
        summary="用户登录/注册",
        description="用户登录获取认证token，如果用户不存在则自动创建",
        request=UserLoginSerializer,
        responses={200: "登录成功", 201: "注册并登录成功", 400: "参数错误"}
    )
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            try:

                # 尝试获取现有用户
                user = User.objects.get(username=username)
                # 验证密码
                if user.check_password(password):
                    token, _ = Token.objects.get_or_create(user=user)
                    # 设置token过期时间为4小时
                    token.created = timezone.now()
                    token.save()

                    return ApiResponse(data={
                        'user_id': user.id,
                        'username': user.username,
                        'user_nickname': user.user_nickname,
                        'token': token.key,
                        'member_level': user.member_level,
                        'expires_in': 14400  # 4小时，单位秒
                    }, message='登录成功')
                else:
                    return ApiResponse(code=401, message='密码错误')
            except User.DoesNotExist:
                # 用户不存在，自动创建新用户
                user = User.objects.create_user(
                    username=username,
                    password=password
                )
                token, _ = Token.objects.get_or_create(user=user)
                # 设置token过期时间为4小时
                token.created = timezone.now()
                token.save()
                return ApiResponse(data={
                    'user_id': user.id,
                    'username': user.username,
                    'user_nickname': user.user_nickname,
                    'token': token.key,
                    'member_level': user.member_level,
                    'expires_in': 14400  # 4小时，单位秒
                }, code=201, message='注册并登录成功')
        return ApiResponse(code=400, message=serializer.errors)

@extend_schema(tags=["用户管理"])
@extend_schema_view(
    list=extend_schema(summary="获取用户列表",responses={200: UserSerializer(many=True)}
    ),
    retrieve=extend_schema(summary="获取用户详情,返回是否关注，房间session",responses={200: UserSerializer, 404: "用户不存在"}
    ),
    update=extend_schema(
        summary="更新用户",description="通过id除username都可变",request=UserSerializer),
    partial_update=extend_schema(summary="部分更新用户",request=UserSerializer),
    destroy=extend_schema(summary="删除用户",description="删除指定用户，仅管理员可操作",responses={204: "删除成功", 404: "用户不存在"}
    )
)
class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_queryset(self):
        """数据权限过滤"""
        user = self.request.user
        return User.objects.all()



# 新增用户组管理视图集
@extend_schema(tags=["用户组管理"])
@extend_schema_view(
    list=extend_schema(summary="获取用户组列表",description="返回所有用户组，仅管理员可访问",responses={200: GroupSerializer(many=True)}),
    create=extend_schema(summary="创建用户组",request=GroupSerializer,responses={201: GroupSerializer}),
    retrieve=extend_schema(summary="获取用户组详情",responses={200: GroupSerializer, 404: "用户组不存在"}),
    update=extend_schema(summary="全量更新用户组",request=GroupSerializer),
    partial_update=extend_schema(summary="部分更新用户组",request=GroupSerializer),
    destroy=extend_schema(summary="删除用户组",description="删除指定用户组，仅管理员可操作",responses={204: "删除成功", 404: "用户组不存在"}
    )
)
class GroupViewSet(BaseViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]  # 仅管理员可操作用户组


