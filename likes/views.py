from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse
from .models import Like
from .serializers import LikeSerializer, LikeToggleSerializer
from contents.models import Content
# @extend_schema_view(
#     list=extend_schema(summary='获取点赞列表', tags=['点赞管理']),
#     retrieve=extend_schema(summary='获取点赞详情', tags=['点赞管理']),
#     destroy=extend_schema(summary='删除点赞', tags=['点赞管理'])
# )
class DynamicLikeViewSet(BaseViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @extend_schema(
        summary='动态点赞/取消点赞切换',
        tags=['点赞管理'],
        request=LikeToggleSerializer,
        responses={200: LikeSerializer}
    )
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        点赞/取消点赞切换接口
        如果未点赞则创建点赞记录，如果已点赞则取消点赞
        """
        serializer = LikeToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_id = serializer.validated_data['target_id']
        user_id = request.user.id
        # 验证目标是否存在
        from societies.models import Dynamic
        try:
            Dynamic.objects.get(id=target_id)
        except Dynamic.DoesNotExist:
            return ApiResponse(code=400, message="目标动态不存在")

        # 查找是否已有点赞记录
        like, created = Like.objects.get_or_create(
            type='dynamic',
            target_id=target_id,
            user_id=user_id,
            defaults={
                'status': 'active'
            }
        )
        if not created:
            # 如果记录已存在，切换状态
            if like.status == 'active':
                like.status = 'inactive'
                message = "取消点赞成功"
            else:
                like.status = 'active'
                message = "点赞成功"
            like.save()
        else:
            message = "点赞成功"
        # 返回更新后的点赞信息
        result_serializer = LikeSerializer(like)
        return ApiResponse(data=result_serializer.data, message=message)

    def get_queryset(self):
        # 只返回当前用户的点赞记录
        if self.request.user.is_authenticated:
            return Like.objects.filter(user_id=self.request.user.id)
        return Like.objects.none()


# @extend_schema_view(
#     list=extend_schema(summary='获取内容点赞列表', tags=['点赞管理']),
#     retrieve=extend_schema(summary='获取内容点赞详情', tags=['点赞管理']),
#     destroy=extend_schema(summary='删除内容点赞', tags=['点赞管理'])
# )
class ContentLikeViewSet(BaseViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @extend_schema(
        summary='内容点赞/取消点赞切换',
        tags=['点赞管理'],
        request=LikeToggleSerializer,
        responses={200: LikeSerializer}
    )
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        内容点赞/取消点赞切换接口
        """
        serializer = LikeToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_id = serializer.validated_data['target_id']
        user_id = request.user.id

        # 验证目标内容是否存在
        try:
            Content.objects.get(id=target_id)
        except Content.DoesNotExist:
            return ApiResponse(code=400, message="目标内容不存在")

        # 查找是否已有点赞记录
        like, created = Like.objects.get_or_create(
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
            if like.status == 'active':
                like.status = 'inactive'
                message = "内容点赞取消点赞成功"
            else:
                like.status = 'active'
                message = "内容点赞成功"
            like.save()
        else:
            message = "点赞成功内容"
        # 返回更新后的点赞信息
        result_serializer = LikeSerializer(like)
        return ApiResponse(data=result_serializer.data, message=message)
    def perform_create(self, serializer):
        # 自动设置当前用户信息和类型
        serializer.save(user_id=self.request.user.id)
    def get_queryset(self):
        # 只返回当前用户的内容点赞记录
        if self.request.user.is_authenticated:
            return Like.objects.filter(user_id=self.request.user.id)
        return Like.objects.none()

