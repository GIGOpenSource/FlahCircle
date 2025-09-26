from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse
from .models import Rating
from .serializers import RatingSerializer, RatingCreateSerializer, RatingGetSerializer
from contents.models import Content


@extend_schema_view(
    list=extend_schema(
        summary='获取评分列表',
        tags=['评分管理'],
    ),
    retrieve=extend_schema(
        summary='获取评分详情',
        tags=['评分管理'],
    ),
)
class RatingViewSet(BaseViewSet):
    """
    评分功能视图集
    """
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_queryset(self):
        # 只返回当前用户的评分记录
        if self.request.user.is_authenticated:
            return Rating.objects.filter(user=self.request.user)
        return Rating.objects.none()

    @extend_schema(
        summary='对内容进行评分',
        tags=['评分管理'],
        request=RatingCreateSerializer,
        responses={200: RatingSerializer}
    )
    @action(detail=False, methods=['post'], url_path='rate')
    def rate(self, request):
        """
        对内容进行评分接口
        用户可以对内容进行1-5分的评分
        """
        serializer = RatingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content_id = serializer.validated_data['content_id']
        score = serializer.validated_data['score']
        user = request.user
        # 验证内容是否存在
        try:
            content = Content.objects.get(id=content_id)
        except Content.DoesNotExist:
            return ApiResponse(code=400, message="目标内容不存在")

        try:
            # 如果已存在评分记录，则更新
            rating = Rating.objects.get(user=user, content=content)
            old_score = rating.score
            rating.score = score
            rating.save()
            created = False
            message = "评分更新成功"
        except Rating.DoesNotExist:
            # 如果不存在评分记录，则创建新记录
            rating = Rating.objects.create(
                user=user,
                content=content,
                score=score
            )
            created = True
            message = "评分成功"
            # 返回评分信息
        result_serializer = RatingSerializer(rating)

        return ApiResponse(data=result_serializer.data, message=message)

    def perform_create(self, serializer):
        # 自动设置当前用户
        serializer.save(user=self.request.user)

    @extend_schema(
        summary='获取内容评分详情',
        tags=['评分管理'],
        request=RatingGetSerializer,
        responses={200: RatingSerializer}
    )
    @action(detail=False, methods=['post'], url_path='get-rating')
    def get_rating(self, request):
        """
        获取内容评分详情接口
        通过内容ID和当前用户ID获取评分信息
        """
        serializer = RatingGetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content_id = serializer.validated_data['content_id']
        user = request.user

        # 验证内容是否存在
        try:
            content = Content.objects.get(id=content_id)
        except Content.DoesNotExist:
            return ApiResponse(code=400, message="目标内容不存在")

        # 获取评分记录
        try:
            rating = Rating.objects.get(user=user, content=content)
            result_serializer = RatingSerializer(rating)
            return ApiResponse(data=result_serializer.data, message="获取评分详情成功")
        except Rating.DoesNotExist:
            return ApiResponse(code=404, message="未找到评分记录")
