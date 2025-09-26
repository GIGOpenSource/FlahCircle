from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from middleware.base_views import BaseViewSet
from middleware.utils import CustomPagination, ApiResponse
from tags.models import Tag
from tags.serializers import TagSerializer, UserRecommendationSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from user.models import User

UserModel = get_user_model()

@extend_schema_view(
    list=extend_schema(summary='获取兴趣标签列表（分页)',tags=['兴趣标签管理'],
        parameters=[OpenApiParameter(name='follower_id', description='兴趣标签类型过滤'),
        OpenApiParameter(name='followee_id', description='兴趣标签描述过滤'),]
    ),
    retrieve=extend_schema(summary='获取兴趣标签详情',tags=['兴趣标签管理']),
    create=extend_schema(summary='创建兴趣标签',tags=['兴趣标签管理']),
    update=extend_schema(summary='更新兴趣标签',tags=['兴趣标签管理']),
    partial_update=extend_schema(summary='部分更新兴趣标签',tags=['兴趣标签管理']),
    destroy=extend_schema(summary='删除兴趣标签',tags=['兴趣标签管理'])
)
class TagViewSet(BaseViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = CustomPagination
    search_fields = ['name']
    ordering = ['-usage_count']

    @extend_schema(
        summary='推荐博主',
        tags=['兴趣标签管理'],
        parameters=[
            OpenApiParameter(name='tags', description='标签ID列表，多个ID用逗号分隔', required=True),
            OpenApiParameter(name='page', description='页码', required=False),
            OpenApiParameter(name='page_size', description='每页数量', required=False)
        ],
        responses={200: UserRecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='recommend-users')
    def recommend_users(self, request):
        """
        根据标签推荐博主
        通过传入的标签ID数组，匹配具有相同标签的用户，并按关注者数量排序
        """
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            return ApiResponse(code=401, message="用户未认证")
        tags_param = request.query_params.get('tags', None)
        if not tags_param:
            return ApiResponse(code=400, message="请提供标签ID参数")

        try:
            # 处理URL编码的逗号分隔参数
            import urllib.parse
            decoded_tags = urllib.parse.unquote(tags_param)
            tag_ids = [int(tag_id) for tag_id in decoded_tags.split(',')]
        except ValueError:
            return ApiResponse(code=400, message="标签ID格式错误，请提供有效的数字ID")

        # 验证标签是否存在
        existing_tags = Tag.objects.filter(id__in=tag_ids)
        if existing_tags.count() != len(tag_ids):
            return ApiResponse(code=400, message="部分标签ID不存在")
            # 获取当前用户已关注的用户ID列表
        from follows.models import Follow
        followed_users = Follow.objects.filter(
            follower_id=request.user.id,
            status='active'
        ).values_list('followee_id', flat=True)

        # 获取具有这些标签的用户，按关注者数量排序
        # 过滤掉当前用户自己和已关注的用户
        users = User.objects.filter(
            tags__in=tag_ids,
            is_active=True
        ).exclude(
            id=request.user.id  # 排除自己
        ).exclude(
            id__in=followed_users  # 排除已关注的用户
        ).distinct().order_by('-followers_count')

        # 分页处理
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = UserRecommendationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserRecommendationSerializer(users, many=True)
        return ApiResponse(serializer.data)

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
