from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from comments.models import Comment
from comments.serializers import CommentSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from contents.models import Content
from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse, CustomPagination
from societies.models import Dynamic



class CommentViewSet(BaseViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_id', 'type', 'parent_comment_id']
    search_fields = ['content', 'user_nickname']
    ordering_fields = ['create_time', 'like_count']
    # ordering = ['-create_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        # 获取target_id参数
        target_id = self.request.query_params.get('target_id', None)
        if target_id is not None:
            queryset = queryset.filter(target_id=target_id)
        return queryset
    def perform_create(self, serializer):
        # 自动设置当前用户信息
        serializer.save(user_id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse(message="评论删除成功")

    def list(self, request, *args, **kwargs):
        # 获取过滤后的查询集
        # 检查是否提供了target_id参数
        target_id = self.request.query_params.get('target_id', None)
        if target_id is None:
            return ApiResponse(code=400, message="缺少target_id参数")
        queryset = self.filter_queryset(self.get_queryset())
        # 获取分页器实例
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 获取当前用户点赞的评论ID列表
            context_data = self.get_user_context_data(request)
            serializer = self.get_serializer(page, many=True, context=context_data)
            # 使用自定义分页响应
            return self.get_paginated_response(serializer.data)
            # 如果没有分页，返回普通响应
            # 获取当前用户点赞的评论ID列表
        context_data = self.get_user_context_data(request)
        serializer = self.get_serializer(queryset, many=True, context=context_data)
        return ApiResponse(serializer.data)

    def get_user_context_data(self, request):
        """获取当前用户点赞的评论数据"""
        context_data = {
            'request': request,
            'liked_comment_ids': []
        }

        if request.user.is_authenticated:
            # 获取点赞数据 - 当前用户点赞的评论ID列表
            from likes.models import Like
            liked_comments = Like.objects.filter(
                user_id=request.user.id,
                type='comment',
                status='active'
            ).values_list('target_id', flat=True)
            context_data['liked_comment_ids'] = list(liked_comments)

        return context_data

@extend_schema(tags=["评论管理 内容"])
@extend_schema_view(
    list=extend_schema(
        summary='获取内容评论列表(必传target_id)只返回父级评论',
        parameters=[
            OpenApiParameter(
                name='ordering',
                description='排序字段，例如: -create_time(最新), create_time(最早)，-like_count（推荐）',
                required=False,
                type=str
            )
        ]
    ),
    create=extend_schema(summary='创建内容评论'),
    destroy=extend_schema(summary='删除内容评论')
)
class ContentCommentViewSet(CommentViewSet):
    """
    专门处理内容评论的ViewSet
    """

    def get_user_context_data(self, request):
        """获取当前用户点赞的评论数据"""
        context_data = {
            'request': request,
            'liked_comment_ids': []
        }

        if request.user.is_authenticated:
            # 获取点赞数据 - 当前用户点赞的评论ID列表
            from likes.models import Like
            liked_comments = Like.objects.filter(
                user_id=request.user.id,
                type='comment',
                status='active'
            ).values_list('target_id', flat=True)
            context_data['liked_comment_ids'] = list(liked_comments)

        return context_data

    def perform_create(self, serializer):
        # 保存评论并更新Content的comment_count
        comment = serializer.save(user_id=self.request.user.id, type='content')
        # 更新Content表的comment_count
        try:
            content = Content.objects.get(id=comment.target_id)
            content.comment_count = content.comment_count + 1
            content.save(update_fields=['comment_count'])
        except Content.DoesNotExist:
            pass
    def perform_destroy(self, instance):
        # 减少Content表的comment_count
        target_id = instance.target_id
        super().perform_destroy(instance)

        try:
            content = Content.objects.get(id=target_id)
            content.comment_count = max(0, content.comment_count - 1)
            content.save(update_fields=['comment_count'])
        except Content.DoesNotExist:
            pass

@extend_schema(tags=["评论管理 动态"])
@extend_schema_view(
    list=extend_schema(
        summary='获取动态评论列表 （必传target_id）只返回父级评论',
        parameters=[
            OpenApiParameter(
                name='ordering',
                description='排序字段，例如: -create_time(最新), create_time(最早),-like_count（推荐）',
                required=False,
                type=str
            )
        ]
    ),
    create=extend_schema(summary='创建动态评论'),
    destroy=extend_schema(summary='删除动态评论')
)
class DynamicCommentViewSet(CommentViewSet):
    """
    专门处理动态评论的ViewSet
    """
    def get_queryset(self):
        """
        默认只获取动态评论（type='dynamic'）和顶级评论（parent_comment_id=0）
        """
        queryset = super().get_queryset()
        # 筛选type为dynamic的评论
        queryset = queryset.filter(type='dynamic')
        # 筛选顶级评论（parent_comment_id为0或None）
        queryset = queryset.filter(parent_comment_id=0)
        return queryset

    def get_user_context_data(self, request):
        """获取当前用户点赞的评论数据"""
        context_data = {
            'request': request,
            'liked_comment_ids': []
        }

        if request.user.is_authenticated:
            # 获取点赞数据 - 当前用户点赞的评论ID列表
            from likes.models import Like
            liked_comments = Like.objects.filter(
                user_id=request.user.id,
                type='comment',
                status='active'
            ).values_list('target_id', flat=True)
            context_data['liked_comment_ids'] = list(liked_comments)

        return context_data

    def perform_create(self, serializer):
        # 保存评论并更新Dynamic的comment_count
        comment = serializer.save(user_id=self.request.user.id, type='dynamic')

        # 更新Dynamic表的comment_count
        try:
            dynamic = Dynamic.objects.get(id=comment.target_id)
            dynamic.comment_count = dynamic.comment_count + 1
            dynamic.save(update_fields=['comment_count'])
        except Dynamic.DoesNotExist:
            pass

    def perform_destroy(self, instance):
        # 减少Dynamic表的comment_count
        target_id = instance.target_id
        super().perform_destroy(instance)

        try:
            dynamic = Dynamic.objects.get(id=target_id)
            dynamic.comment_count = max(0, dynamic.comment_count - 1)
            dynamic.save(update_fields=['comment_count'])
        except Dynamic.DoesNotExist:
            pass