from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import filters
from rest_framework.decorators import action

from comments.models import Comment
from follows.models import Follow
from likes.models import Like
from middleware.base_views import BaseViewSet
from middleware.utils import CustomPagination, ApiResponse
from societies.models import Dynamic
from societies.serializers import SocialDynamicSerializer, SocialDynamicWithFollowSerializer

@extend_schema(tags=["社区动态"])
@extend_schema_view(
    list=extend_schema(summary='获取动态视频列表，关注点赞收藏',tags=['社区动态'],
        parameters=[OpenApiParameter(name='type', description='视频分类 长短视频'),
        OpenApiParameter(name='tabs', description='暂时不用'),
        OpenApiParameter(name='ordering',description='排序字段，例如: -like_count(最热), -create_time(最新)'),]
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
    filterset_fields = ['type', 'tabs', 'user']

    ordering_fields = ['create_time', 'like_count', 'comment_count', 'favorite_count']
    ordering = ['-create_time']
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

    def get_queryset(self):
        queryset = super().get_queryset()

        # 检查是否是个人动态请求
        if self.action == 'personal':
            # 只返回当前用户的动态
            if self.request.user.is_authenticated:
                queryset = queryset.filter(user_id=self.request.user)
            else:
                # 如果用户未认证，返回空查询集
                queryset = queryset.none()

        return queryset

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

    def perform_create(self, serializer):
        # 自动设置当前用户
        serializer.save(user=self.request.user)
    @extend_schema(
        summary='分享动态视频',
        tags=['社区动态']
    )

    @action(detail=False, methods=['post'], url_path='share')
    def share(self, request):
        print(request.data.get('id'))
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

@extend_schema(tags=["社区动态"])
@extend_schema_view(
    list=extend_schema(summary='获取关注的动态', tags=['社区动态'])
)
class FollowedDynamicViewSet(BaseViewSet):
    """
    关注动态ViewSet
    通过用户ID获取该用户关注的人发布的动态
    """
    queryset = Dynamic.objects.all()
    serializer_class = SocialDynamicSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'tabs']
    search_fields = ['title', 'content']
    ordering_fields = ['create_time', 'update_time', 'like_count', 'comment_count']
    ordering = ['-create_time']

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
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            return ApiResponse(code=401, message="用户未认证")

        # 获取当前用户ID
        current_user = request.user

        # 获取该用户关注的用户ID列表
        followed_users = Follow.objects.filter(
            follower_id=current_user.id,
            status='active'
        ).values_list('followee_id', flat=True)

        # 获取关注用户发布的动态
        queryset = Dynamic.objects.filter(user__in=followed_users)
        queryset = self.filter_queryset(queryset)

        # 获取当前登录用户的相关数据（用于显示是否关注、点赞、收藏等状态）
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

@extend_schema(tags=["社区动态"])
@extend_schema_view(
    list=extend_schema(summary='获取互动消息', tags=['社区动态'])
)
class InteractionMessageViewSet(BaseViewSet):
    """
    互动消息ViewSet
    获取用户的点赞 和 评论互动消息
    """
    pagination_class = CustomPagination
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
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            return ApiResponse(code=401, message="用户未认证")

        # 获取当前用户ID
        current_user = request.user

        # 获取点赞消息 - 其他用户点赞当前用户发布的内容
        like_messages = Like.objects.filter(
            target_author_id=current_user.id,
            type='dynamic',
            status='active'
        ).exclude(user_id=current_user.id)

        # 获取评论消息 - 其他用户评论当前用户发布的内容
        # 首先获取当前用户发布的动态ID
        user_dynamics = Dynamic.objects.filter(user=current_user).values_list('id', flat=True)  # 修改为'user=current_user'
        comment_messages = Comment.objects.filter(
            target_id__in=user_dynamics
        ).exclude(user_id=current_user.id)

        # 构建统一的消息格式
        messages = []

        # 处理点赞消息
        for like in like_messages:
            try:
                dynamic = Dynamic.objects.get(id=like.target_id)
                is_liked = like.status == 'active',
                messages.append({
                    'id': like.id,
                    'type': 'like',
                    'user_id': like.user_id,
                    'user_nickname': like.user_nickname,
                    'user_avatar': like.user_avatar,
                    'target_id': like.target_id,
                    'is_liked': is_liked,
                    'target_title': like.target_title or dynamic.title,
                    'target_content': getattr(dynamic, 'content', '')[:100] + '...' if getattr(dynamic, 'content','') else '',
                    'create_time': like.create_time,
                    'dynamic': SocialDynamicSerializer(dynamic).data
                })
            except Dynamic.DoesNotExist:
                continue

        # 处理评论消息
        for comment in comment_messages:
            try:
                dynamic = Dynamic.objects.get(id=comment.target_id)
                # 检查当前登录用户是否对这个动态点过赞
                is_liked = False
                if request.user.is_authenticated:
                    try:
                        # from likes.models import Like
                        like = Like.objects.get(
                            type='dynamic',
                            target_id=comment.target_id,
                            user_id=request.user.id
                        )
                        is_liked = like.status == 'active'
                    except Like.DoesNotExist:
                        pass
                messages.append({
                    'id': comment.id,
                    'type': 'comment',
                    'user_id': comment.user_id,
                    'user_nickname': comment.user_nickname,
                    'user_avatar': comment.user_avatar,
                    'target_id': comment.target_id,
                    'target_title': dynamic.title,
                    'target_content': comment.content[:100] + '...' if comment.content else '',
                    'is_liked': is_liked,
                    'create_time': comment.create_time,
                    'dynamic': SocialDynamicSerializer(dynamic).data
                })
            except Dynamic.DoesNotExist:
                continue

        # 按创建时间排序
        messages.sort(key=lambda x: x['create_time'], reverse=True)
        # 获取当前登录用户的相关数据（用于显示是否关注、点赞、收藏等状态）
        context_data = self.get_user_context_data(request)
        # 应用分页（将列表转换为可分页的对象）
        from django.core.paginator import Paginator
        from rest_framework.request import Request

        # 获取分页参数
        page_size = int(request.query_params.get('pageSize', 20))
        current_page = int(request.query_params.get('currentPage', 1))

        # 手动分页
        paginator = Paginator(messages, page_size)
        page_obj = paginator.get_page(current_page)

        # 序列化分页数据
        result_data = []
        for msg in page_obj.object_list:
            result_data.append({
                'id': msg['id'],
                'type': msg['type'],
                'user': {
                    'id': msg['user_id'],
                    'nickname': msg['user_nickname'],
                    'avatar': msg['user_avatar'],
                },
                'target': {
                    'id': msg['target_id'],
                    'title': msg['target_title'],
                    'content': msg['target_content'],
                },
                'is_liked': msg['is_liked'],
                'dynamic': msg['dynamic'],
                'create_time': msg['create_time'].strftime('%Y-%m-%d %H:%M:%S'),
            })

        # 返回分页响应
        return ApiResponse({
            'pagination': {
                'page': page_obj.number,
                'page_size': page_size,
                'total': paginator.count,
                'total_pages': paginator.num_pages
            },
            'results': result_data
        })