# user/views.py
from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, generics, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model

from middleware.base_views import BaseViewSet
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, GroupSerializer
from rest_framework.authtoken.models import Token
from middleware.utils import ApiResponse



User = get_user_model()


@extend_schema_view(
    create=extend_schema(
        summary="用户注册",
        description="用户自主注册账号，返回认证token",
        request=UserRegisterSerializer,
        responses={201: "注册成功", 400: "参数错误"}
    )
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
                'token': token.key
            })
        return ApiResponse(code=400, message=serializer.errors)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return ApiResponse(code=200, data=serializer.data, message="用户列表获取成功")
                # return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return ApiResponse(code=200, data=serializer.data, message="用户列表获取成功")
        except Exception as e:
            return ApiResponse(code=500, message=f"获取广告列表失败: {str(e)}")
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return ApiResponse(data=serializer.data, message="广告详情获取成功")
        except Exception as e:
            return ApiResponse(code=500, message=f"获取广告详情失败: {str(e)}")
@extend_schema(tags=["用户管理"])
class CustomLoginView(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]
    @extend_schema(
        operation_id="user-login",
        summary="用户登录",
        description="用户登录获取认证token",
        request=UserLoginSerializer,
        responses={200: "登录成功", 401: "认证失败"}
    )
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    token, _ = Token.objects.get_or_create(user=user)
                    return ApiResponse(data={
                        'user_id': user.id,
                        'username': user.username,
                        'token': token.key,
                        'member_level': user.member_level  # 返回会员等级
                    })
                return ApiResponse(code=401, message='密码错误')
            except User.DoesNotExist:
                return ApiResponse(code=401, message='用户不存在')
        return ApiResponse(code=400, message=serializer.errors)

@extend_schema(tags=["用户管理"])
@extend_schema_view(
    list=extend_schema(
        summary="获取用户列表",
        description="返回系统所有用户，仅管理员可访问",
        responses={200: UserSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="获取用户详情",
        description="根据ID获取用户详情，管理员可查看所有，用户可查看自己",
        responses={200: UserSerializer, 404: "用户不存在"}
    ),
    update=extend_schema(
        summary="全量更新用户",
        description="全量更新用户信息，管理员可更新所有，用户可更新自己",
        request=UserSerializer
    ),
    partial_update=extend_schema(
        summary="部分更新用户",
        description="部分更新用户信息，管理员可更新所有，用户可更新自己",
        request=UserSerializer
    ),
    destroy=extend_schema(summary="删除用户",description="删除指定用户，仅管理员可操作",responses={204: "删除成功", 404: "用户不存在"}
    )
)
class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # def get_permissions(self):
    #     """动态权限控制"""
    #     if self.action in ['list', 'destroy']:
    #         # 列表和删除仅管理员可操作
    #         return [permissions.IsAdminUser()]
    #     # 其他操作需要登录（本人或管理员）
    #     return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """数据权限过滤"""
        user = self.request.user
        # if user.is_admin_role():  # 使用模型中定义的管理员判断方法
        #     return User.objects.all()
        return User.objects.all()
        # return User.objects.filter(id=user.id)  # 普通用户仅能查看自己
    # def check_object_permissions(self, request, obj):
    #     """对象级权限检查"""
    #     if request.user.is_admin_role():
    #         return True
    #     return obj == request.user  # 普通用户仅能操作自己


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