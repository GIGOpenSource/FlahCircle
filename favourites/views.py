from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse
from .models import Favorite
from .serializers import FavoriteSerializer, FavoriteToggleSerializer
from societies.models import Dynamic
from contents.models import Content
# @extend_schema_view(
#     list=extend_schema(summary='获取收藏', tags=['收藏管理'],
#         parameters=[{
#             'name': 'type',
#             'in': 'query',
#             'description': 'type字段过滤',
#             'schema': {'type': 'string'}
#         }]
#     ),
#     retrieve=extend_schema(summary='获取收藏详情', tags=['收藏管理']),
#     create=extend_schema(summary='创建收藏', tags=['收藏管理']),
#     update=extend_schema(summary='更新收藏', tags=['收藏管理']),
#     partial_update=extend_schema(summary='部分更新收藏', tags=['收藏管理']),
#     destroy=extend_schema(summary='删除收藏', tags=['收藏管理'])
# )
class DynamicFavoriteViewSet(BaseViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    @extend_schema(
        summary='收藏/取消收藏切换',
        tags=['收藏管理'],
        request=FavoriteToggleSerializer,
        responses={200: FavoriteSerializer}
    )
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        收藏/取消收藏切换接口
        如果未收藏则创建收藏记录，如果已收藏则取消收藏
        """
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_id = serializer.validated_data['target_id']
        user_id = request.user.id

        # 验证目标是否存在
        try:
            dynamic = Dynamic.objects.get(id=target_id)
        except Dynamic.DoesNotExist:
            return ApiResponse(code=400, message="目标动态不存在")

        # 查找是否已存在收藏记录
        favorite, created = Favorite.objects.get_or_create(
            target_id=target_id,
            user_id=user_id,
            defaults={
                'status': 'active',
                'type': 'dynamic'  # 默认类型
            }
        )
        message = ""
        if not created:
            # 如果记录已存在，切换状态
            if favorite.status == 'active':
                favorite.status = 'inactive'
                message = "取消收藏成功"
            else:
                favorite.status = 'active'
                message = "收藏成功"
            favorite.save()
        else:
            message = "收藏成功"

        # 返回更新后的收藏信息
        result_serializer = FavoriteSerializer(favorite)
        return ApiResponse(data=result_serializer.data, message=message)

    def get_queryset(self):
        # 只返回当前用户的收藏记录
        if self.request.user.is_authenticated:
            return Favorite.objects.filter(user_id=self.request.user.id)
        return Favorite.objects.none()

    def perform_create(self, serializer):
        # 自动设置当前用户信息
        serializer.save(user_id=self.request.user.id)

@extend_schema_view(
    list=extend_schema(summary='获取内容收藏', tags=['内容收藏管理']),
    retrieve=extend_schema(summary='获取内容收藏详情', tags=['内容收藏管理']),
    create=extend_schema(summary='创建内容收藏', tags=['内容收藏管理']),
    # update=extend_schema(summary='更新内容收藏', tags=['内容收藏管理']),
    # partial_update=extend_schema(summary='部分更新内容收藏', tags=['内容收藏管理']),
    # destroy=extend_schema(summary='删除内容收藏', tags=['内容收藏管理'])
)
class ContentFavoriteViewSet(BaseViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    def get_queryset(self):
        # 只返回当前用户的内容收藏记录
        if self.request.user.is_authenticated:
            return Favorite.objects.filter(user_id=self.request.user.id, type='content')
        return Favorite.objects.none()

    @extend_schema(
        summary='内容收藏/取消收藏切换',
        tags=['收藏管理'],
        request=FavoriteToggleSerializer,
        responses={200: FavoriteSerializer}
    )
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        内容收藏/取消收藏切换接口
        """
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_id = serializer.validated_data['target_id']
        user_id = request.user.id

        # 验证目标内容是否存在
        try:

            Content.objects.get(id=target_id)
        except Content.DoesNotExist:
            return ApiResponse(code=400, message="目标内容不存在")

        # 查找是否已存在收藏记录
        favorite, created = Favorite.objects.get_or_create(
            type='content',
            target_id=target_id,
            user_id=user_id,
            defaults={
                'status': 'active'
            }
        )

        message = ""
        if not created:
            # 如果记录已存在，切换状态
            if favorite.status == 'active':
                favorite.status = 'inactive'
                message = "取消收藏成功"
            else:
                favorite.status = 'active'
                message = "收藏成功"
            favorite.save()
        else:
            message = "收藏成功"

        # 返回更新后的收藏信息
        result_serializer = FavoriteSerializer(favorite)
        return ApiResponse(data=result_serializer.data, message=message)

    def perform_create(self, serializer):
        # 自动设置当前用户信息和类型
        serializer.save(user_id=self.request.user.id, type='content')


@extend_schema_view(
    list=extend_schema(summary='获取内容收藏', tags=['收藏管理']),
    retrieve=extend_schema(summary='获取内容收藏详情', tags=['收藏管理']),
    # create=extend_schema(summary='创建内容收藏', tags=['收藏管理']),
    # update=extend_schema(summary='更新内容收藏', tags=['收藏管理']),
    # partial_update=extend_schema(summary='部分更新内容收藏', tags=['收藏管理']),
    # destroy=extend_schema(summary='删除内容收藏', tags=['收藏管理'])
)
class ContentFavoriteViewSet(BaseViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        # 只返回当前用户的内容收藏记录
        if self.request.user.is_authenticated:
            return Favorite.objects.filter(user_id=self.request.user.id, type='content')
        return Favorite.objects.none()

    @extend_schema(
        summary='内容收藏/取消收藏切换',
        tags=['收藏管理'],
        request=FavoriteToggleSerializer,
        responses={200: FavoriteSerializer}
    )
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        内容收藏/取消收藏切换接口
        """
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_id = serializer.validated_data['target_id']
        user_id = request.user.id

        # 验证目标内容是否存在
        try:
            from contents.models import Content
            Content.objects.get(id=target_id)
        except Content.DoesNotExist:
            return ApiResponse(code=400, message="目标内容不存在")

        # 查找是否已存在收藏记录
        favorite, created = Favorite.objects.get_or_create(
            type='content',
            target_id=target_id,
            user_id=user_id,
            defaults={
                'status': 'active'
            }
        )

        message = ""
        if not created:
            # 如果记录已存在，切换状态
            if favorite.status == 'active':
                favorite.status = 'inactive'
                message = "取消收藏成功"
            else:
                favorite.status = 'active'
                message = "收藏成功"
            favorite.save()
        else:
            message = "收藏成功"

        # 返回更新后的收藏信息
        result_serializer = FavoriteSerializer(favorite)
        return ApiResponse(data=result_serializer.data, message=message)

    def perform_create(self, serializer):
        # 自动设置当前用户信息和类型
        serializer.save(user_id=self.request.user.id, type='content')

