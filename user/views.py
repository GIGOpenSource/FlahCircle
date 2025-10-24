from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status, generics, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from middleware.base_views import BaseViewSet
from middleware.permissions import IsAdminRole, IsCreator, IsAdminOrCreator
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, GroupSerializer
from rest_framework.authtoken.models import Token
from middleware.utils import ApiResponse, CustomPagination
from rest_framework.decorators import action
from .models import UserPurchase
from .serializers import UserPurchaseSerializer

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
                        'is_staff': user.is_staff,
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
    list=extend_schema(summary="获取用户列表", parameters=[
        OpenApiParameter(name='status', description='账号状态'),
        OpenApiParameter(name='member_level', description='账号状态'),
        OpenApiParameter(name='phone', description='电话号'),
        OpenApiParameter(name='id', description='ID'),
        OpenApiParameter(name='user_nickname', description='用户名'),
        OpenApiParameter(name='search', description='模糊搜索字段：id 用户ID、昵称 user_nickname、手机号phone'),

    ], responses={200: UserSerializer(many=True), }
                       ),
    retrieve=extend_schema(summary="获取用户详情,返回是否关注，房间session",
                           responses={200: UserSerializer, 404: "用户不存在"}
                           ),
    update=extend_schema(
        summary="更新用户", description="通过id除username都可变", request=UserSerializer),
    partial_update=extend_schema(summary="部分更新用户", request=UserSerializer),
    destroy=extend_schema(summary="删除用户", description="删除指定用户，仅管理员可操作",
                          responses={204: "删除成功", 404: "用户不存在"}
                          )
)
class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id', 'status', 'member_level', 'phone', 'id', 'user_nickname', ]

    # search_fields = ['id','user_nickname', 'phone']
    def get_permissions(self):
        """
        为不同的操作设置不同的权限要求
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            # 管理员或个人创作者可以修改和删除用户
            permission_classes = [IsAdminOrCreator]
        else:
            # 其他操作使用基础认证权限
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        # 获取过滤后的查询集
        queryset = self.filter_queryset(self.get_queryset())
        # 获取分页器实例
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 使用自定义分页响应
            return self.get_paginated_response(serializer.data)
        # 如果没有分页，返回普通响应
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse(serializer.data)


# 新增用户组管理视图集
@extend_schema(tags=["用户组管理"])
@extend_schema_view(
    list=extend_schema(summary="获取用户组列表", description="返回所有用户组，仅管理员可访问",
                       responses={200: GroupSerializer(many=True)}),
    create=extend_schema(summary="创建用户组", request=GroupSerializer, responses={201: GroupSerializer}),
    retrieve=extend_schema(summary="获取用户组详情", responses={200: GroupSerializer, 404: "用户组不存在"}),
    update=extend_schema(summary="全量更新用户组", request=GroupSerializer),
    partial_update=extend_schema(summary="部分更新用户组", request=GroupSerializer),
    destroy=extend_schema(summary="删除用户组", description="删除指定用户组，仅管理员可操作",
                          responses={204: "删除成功", 404: "用户组不存在"}
                          )
)
class GroupViewSet(BaseViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]  # 仅管理员可操作用户组


@extend_schema(tags=["用户消费记录"])
class UserPurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = UserPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'content_type']
    ordering_fields = ['purchase_time']
    ordering = ['-purchase_time']

    def get_queryset(self):
        # 管理员可以查看所有消费记录，普通用户只能查看自己的
        user = self.request.user
        if user.is_staff or user.is_superuser or user.is_admin_role():
            return UserPurchase.objects.all().select_related('user')
        return UserPurchase.objects.filter(user=user).select_related('user')

    def get_permissions(self):
        # list操作允许管理员查看所有记录，其他操作仍需认证
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="获取当前用户的消费记录",
        description="返回当前用户的所有消费记录"
    )
    @action(detail=False, methods=['get'], url_path='my-purchases')
    def my_purchases(self, request):
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse(serializer.data)

    @extend_schema(
        summary="按类型获取消费记录",
        description="管理员可查看所有用户的消费记录，普通用户只能查看自己的",
        parameters=[
            OpenApiParameter(name='content_type', description='消费记录类型', required=False),
            OpenApiParameter(name='user', description='用户ID，仅管理员可用', required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="获取消费记录详情",
        description="根据消费记录类型，返回对应的详细信息"
    )
    @action(detail=True, methods=['get'], url_path='detail-info')
    def detail_info(self, request, pk=None):
        try:
            purchase = self.get_object()
            content_type = purchase.content_type
            object_id = purchase.object_id

            # 根据不同类型获取对应的对象
            if content_type == 'content':
                # 查询 contents app 下的模型
                from contents.models import Content
                try:
                    content_obj = Content.objects.get(id=object_id)
                    from contents.serializers import ContentSerializer
                    serializer = ContentSerializer(content_obj)
                    return ApiResponse({
                        'purchase_info': UserPurchaseSerializer(purchase).data,
                        'content_detail': serializer.data
                    })
                except Content.DoesNotExist:
                    return ApiResponse(code=404, message="内容不存在")

            elif content_type == 'dynamic':
                # 查询 societies app 下的模型
                from societies.models import Dynamic
                try:
                    dynamic_obj = Dynamic.objects.get(id=object_id)
                    from societies.serializers import SocialDynamicSerializer
                    serializer = SocialDynamicSerializer(dynamic_obj)
                    return ApiResponse({
                        'purchase_info': UserPurchaseSerializer(purchase).data,
                        'content_detail': serializer.data
                    })
                except Dynamic.DoesNotExist:
                    return ApiResponse(code=404, message="动态不存在")

            elif content_type == 'advertise':
                # 查询 advertisement app 下的模型
                from advertisement.models import Advertisement
                try:
                    ad_obj = Advertisement.objects.get(id=object_id)
                    from advertisement.serializers import AdvertisementSerializer
                    serializer = AdvertisementSerializer(ad_obj)
                    return ApiResponse({
                        'purchase_info': UserPurchaseSerializer(purchase).data,
                        'content_detail': serializer.data
                    })
                except Advertisement.DoesNotExist:
                    return ApiResponse(code=404, message="广告不存在")
            else:
                return ApiResponse(code=400, message="不支持的内容类型")

        except UserPurchase.DoesNotExist:
            return ApiResponse(code=404, message="消费记录不存在")
