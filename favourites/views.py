from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse
from .models import Favorite, Downvote
from .serializers import FavoriteSerializer, FavoriteToggleSerializer, DownvoteSerializer, DownvoteToggleSerializer
from societies.models import Dynamic
from contents.models import Content

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
            type='dynamic',
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

    def get_queryset(self):
        # 只返回当前用户的动态收藏记录
        if self.request.user.is_authenticated:
            return Favorite.objects.filter(user_id=self.request.user.id, type='dynamic')
        return Favorite.objects.none()

    def perform_create(self, serializer):
        # 自动设置当前用户信息
        serializer.save(user_id=self.request.user.id, type='dynamic')

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

class DownvoteViewSet(BaseViewSet):
    """
    点踩功能视图集
    """
    queryset = Downvote.objects.all()
    serializer_class = DownvoteSerializer

    @extend_schema(
        summary='点踩/取消点踩切换',
        tags=['点踩管理'],
        request=DownvoteToggleSerializer,
        responses={200: DownvoteSerializer}
    )
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        点踩/取消点踩切换接口
        如果未点踩则创建点踩记录，如果已点踩则取消点踩
        """
        serializer = DownvoteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_id = serializer.validated_data['target_id']
        user_id = request.user.id

        # 验证目标是否存在
        try:
            content = Content.objects.get(id=target_id)
        except Content.DoesNotExist:
            return ApiResponse(code=400, message="目标内容不存在")

        # 查找是否已存在点踩记录
        downvote, created = Downvote.objects.get_or_create(
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
            if downvote.status == 'active':
                downvote.status = 'inactive'
                message = "取消点踩成功"
            else:
                downvote.status = 'active'
                message = "点踩成功"
            downvote.save()
        else:
            message = "点踩成功"

        # 返回更新后的点踩信息
        result_serializer = DownvoteSerializer(downvote)
        return ApiResponse(data=result_serializer.data, message=message)

    def get_queryset(self):
        # 只返回当前用户的点踩记录
        if self.request.user.is_authenticated:
            return Downvote.objects.filter(user_id=self.request.user.id)
        return Downvote.objects.none()

    def perform_create(self, serializer):
        # 自动设置当前用户信息
        serializer.save(user_id=self.request.user.id)
