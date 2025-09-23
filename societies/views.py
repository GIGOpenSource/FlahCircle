from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import filters
from rest_framework.decorators import action

from middleware.base_views import BaseViewSet
from middleware.utils import CustomPagination, ApiResponse
from societies.models import Dynamic
from societies.serializers import SocialDynamicSerializer, SocialDynamicWithFollowSerializer


@extend_schema_view(
    list=extend_schema(summary='获取动态视频',tags=['社区动态'],
        parameters=[OpenApiParameter(name='type', description='视频分类 长短视频'),
        OpenApiParameter(name='tabs', description='顶端分类： 推荐、关注、最新、发现、精选')]
    ),
    retrieve=extend_schema(summary='获取动态视频详情',tags=['社区动态']),
    create=extend_schema(summary='创建动态视频',tags=['社区动态']),
    update=extend_schema(summary='更新动态视频',tags=['社区动态']),
    partial_update=extend_schema(summary='部分更新动态视频',tags=['社区动态']),
    destroy=extend_schema(summary='删除动态视频',tags=['社区动态'])
)
class DynamicViewSet(BaseViewSet):
    queryset = Dynamic.objects.all()
    serializer_class = SocialDynamicSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'tabs']

    def get_user_context_data(self, request):
        """获取当前用户的相关数据"""
        context_data = {
            'request': request,
            'followed_user_ids': [],
            'liked_dynamic_ids': [],
            'favourite_dynamic_ids': []
        }

        if request.user.is_authenticated:
            # 获取关注数据 - 当前用户关注的用户ID列表
            from follows.models import Follow
            followed_users = Follow.objects.filter(
                follower_id=request.user.id,
                status='active'
            ).values_list('followee_id', flat=True)
            context_data['followed_user_ids'] = list(followed_users)

            # 获取点赞数据 - 当前用户点赞的动态ID列表
            from likes.models import Like
            liked_dynamics = Like.objects.filter(
                user_id=request.user.id,
                type='dynamic',
                status='active'
            ).values_list('target_id', flat=True)
            context_data['liked_dynamic_ids'] = list(liked_dynamics)

            # 获取收藏数据 - 当前用户收藏的动态ID列表
            from favourites.models import Favorite
            favourite_dynamics = Favorite.objects.filter(
                user_id=request.user.id,
                target_id__isnull=False,
                status='active'
            ).values_list('target_id', flat=True)
            context_data['favourite_dynamic_ids'] = list(favourite_dynamics)

        return context_data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 获取当前用户的相关数据
        context_data = self.get_user_context_data(request)

        # 获取分页器实例
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SocialDynamicWithFollowSerializer(page, many=True, context=context_data)
            # 使用自定义分页响应
            return self.get_paginated_response(serializer.data)

        # 如果没有分页，返回普通响应
        serializer = SocialDynamicWithFollowSerializer(queryset, many=True, context=context_data)
        return ApiResponse(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 获取当前用户的相关数据
        context_data = self.get_user_context_data(request)

        # 使用带状态的序列化器
        serializer = SocialDynamicWithFollowSerializer(instance, context=context_data)
        return ApiResponse(serializer.data)
    @action(detail=False, methods=['post'], url_path='share')
    def share(self, request):
        """
        分享动态接口
        传入动态ID，增加该动态的share_count
        """
        dynamic_id = request.data.get('id')

        if not dynamic_id:
            return ApiResponse(code=400, message="缺少动态ID参数")

        try:
            dynamic = Dynamic.objects.get(id=dynamic_id)
            dynamic.share_count = dynamic.share_count + 1
            dynamic.save(update_fields=['share_count'])
            return ApiResponse(
                data={'share_count': dynamic.share_count},
                message="分享成功"
            )
        except Dynamic.DoesNotExist:
            return ApiResponse(code=400, message="动态不存在")
