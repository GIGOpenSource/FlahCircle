from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from contents.models import Content
from contents.serializers import ContentSerializer, ContentWithFollowSerializer
from middleware.base_views import BaseViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from middleware.utils import ApiResponse, CustomPagination


@extend_schema_view(
    list=extend_schema(summary='获取内容列表 搜索筛选 点赞收藏关注',tags=['内容(完成)'],
        parameters=[
            OpenApiParameter(name='type', description='type字段过滤'),
            OpenApiParameter(name='is_vip', description='是否vip视频 true、false'),
            OpenApiParameter(name='time_range', description='时间范围: month(本月), half_year(半年), longer(更久)', required=False),
            OpenApiParameter(name='paid_only', description='仅显示付费内容: true(仅付费), false或不传(全部)',
                             required=False)
        ],
       description='排序字段，例如: -create_time(最新上架),，-favorite_count（收藏量）,-like_count(热门影视)',
       ),
    retrieve=extend_schema(summary='获取内容详情 点赞收藏关注',tags=['内容(完成)']),
    create=extend_schema(summary='创建内容',tags=['内容(完成)']),
    update=extend_schema(summary='更新内容',tags=['内容(完成)']),
    partial_update=extend_schema(summary='部分更新内容',tags=['内容(完成)']),
    destroy=extend_schema(summary='删除内容',tags=['内容(完成)'])
)
class ContentViewSet(BaseViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'tabs', 'is_vip']
    search_fields = ['title', 'description']
    ordering_fields = ['create_time', 'update_time', 'favorite_count','like_count']
    ordering = ['-create_time']

    def perform_create(self, serializer):
        # 自动设置当前用户ID为author_id
        serializer.save(author_id=self.request.user.id)

    def perform_update(self, serializer):
        # 更新时保持原有的author_id
        instance = serializer.instance
        serializer.save(author_id=instance.author_id)

    def get_queryset(self):
        queryset = super().get_queryset()
        # 获取付费解锁参数
        paid_only = self.request.query_params.get('paid_only', None)
        if paid_only and paid_only.lower() == 'true':
            # 筛选price > 0的内容
            queryset = queryset.filter(price__gt=0)
        # 获取时间范围参数
        time_range = self.request.query_params.get('time_range', None)
        if time_range:
            now = timezone.now()
            if time_range == 'month':
                # 本月发布的内容
                start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(create_time__gte=start_of_month)
            elif time_range == 'half_year':
                # 半年内发布的内容
                half_year_ago = now - timedelta(days=180)
                queryset = queryset.filter(create_time__gte=half_year_ago)
            elif time_range == 'longer':
                # 半年以前发布的内容
                half_year_ago = now - timedelta(days=180)
                queryset = queryset.filter(create_time__lt=half_year_ago)

        return queryset

    def get_user_context_data(self, request):
        """获取当前用户的相关数据"""
        context_data = {
            'request': request,
            'followed_user_ids': [],
            'liked_dynamic_ids': [],
            'favourite_dynamic_ids': [],
        }

        if request.user.is_authenticated:
            # 获取关注数据 - 当前用户关注的用户ID列表
            from follows.models import Follow
            followed_users = Follow.objects.filter(
                follower_id=request.user.id,
                status='active'
            ).values_list('followee_id', flat=True)
            context_data['followed_user_ids'] = list(followed_users)

            # 获取点赞数据 - 当前用户点赞的内容ID列表
            from likes.models import Like
            liked_contents = Like.objects.filter(
                user_id=request.user.id,
                type='content',  # 假设内容的type为'content'
                status='active'
            ).values_list('target_id', flat=True)
            context_data['liked_dynamic_ids'] = list(liked_contents)

            # 获取收藏数据 - 当前用户收藏的内容ID列表
            from favourites.models import Favorite
            favourite_contents = Favorite.objects.filter(
                user_id=request.user.id,
                target_id__isnull=False,
                status='active'
            ).values_list('target_id', flat=True)
            context_data['favourite_dynamic_ids'] = list(favourite_contents)

        return context_data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 获取当前用户的相关数据
        context_data = self.get_user_context_data(request)

        # 获取分页器实例
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ContentWithFollowSerializer(page, many=True, context=context_data)
            # 使用自定义分页响应
            return self.get_paginated_response(serializer.data)

        # 如果没有分页，返回普通响应
        serializer = ContentWithFollowSerializer(queryset, many=True, context=context_data)
        return ApiResponse(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 获取当前用户的相关数据
        context_data = self.get_user_context_data(request)

        # 使用序列化器
        serializer = ContentWithFollowSerializer(instance, context=context_data)
        return ApiResponse(serializer.data)

    @extend_schema(
        summary='猜你喜欢',
        tags=['内容'],
        parameters=[
            OpenApiParameter(name='count', description='随机返回数量', type=int, default=10),
            OpenApiParameter(name='currentPage', description='当前页码', type=int, default=1),
            OpenApiParameter(name='pageSize', description='每页数量', type=int, default=20),
        ]
    )
    @action(detail=False, methods=['get'], url_path='guesslike')
    def guess_you_like(self, request):
        """
        猜你喜欢功能
        随机返回一批内容数据，支持分页
        """
        # 获取请求参数
        count = int(request.query_params.get('count', 50))
        # 限制最大返回数量
        count = min(count, 100)
        # 获取随机数据，限制总数
        queryset = Content.objects.all().order_by('?')[:count]
        # 转换为列表以支持分页（因为切片后的QuerySet不支持进一步的分页操作）
        queryset_list = list(queryset)
        # 获取当前用户的相关数据
        context_data = self.get_user_context_data(request)
        # 应用分页
        page = self.paginate_queryset(queryset_list)
        if page is not None:
            serializer = ContentWithFollowSerializer(page, many=True, context=context_data)
            return self.get_paginated_response(serializer.data)

        serializer = ContentWithFollowSerializer(queryset_list, many=True, context=context_data)
        return ApiResponse(serializer.data)

    @extend_schema(
        summary='分享内容',
        tags=['内容管理']
    )
    @action(detail=False, methods=['post'], url_path='share')
    def share(self, request):
        """
        分享内容接口
        传入内容ID，增加该内容的share_count
        """
        content_id = request.data.get('id')
        if not content_id:
            return ApiResponse(code=400, message="缺少内容ID参数")
        try:
            content = Content.objects.get(id=content_id)
            content.share_count = content.share_count + 1
            content.save(update_fields=['share_count'])
            return ApiResponse(
                data={'share_count': content.share_count},
                message="分享成功"
            )
        except Content.DoesNotExist:
            return ApiResponse(code=400, message="内容不存在")
