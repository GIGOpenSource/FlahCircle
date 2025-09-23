from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from comments.models import Comment
from comments.serializers import CommentSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse


@extend_schema_view(
    list=extend_schema(summary='获取评论列表', tags=['评论管理'],
                       parameters=[OpenApiParameter(name='target_id', description='目标ID过滤', type=int)]
                       ),
    # retrieve=extend_schema(summary='获取评论详情', tags=['评论管理']),
    create=extend_schema(summary='创建评论', tags=['评论管理']),
    # update=extend_schema(summary='更新评论', tags=['评论管理']),
    # partial_update=extend_schema(summary='部分更新评论', tags=['评论管理']),
    destroy=extend_schema(summary='删除评论', tags=['评论管理'])
)
class CommentViewSet(BaseViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_id', 'type', 'parent_comment_id']
    search_fields = ['content', 'user_nickname']
    ordering_fields = ['create_time', 'like_count']
    ordering = ['-create_time']

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