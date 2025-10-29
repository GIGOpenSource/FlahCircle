from datetime import datetime
from collections import defaultdict
from pickle import FALSE
from trace import Trace

from django.http import JsonResponse
from rest_framework.decorators import action
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.views import APIView

from comments.models import Comment
from comments.serializers import CommentSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from middleware.autoTask import scheduler
from tools.util_Reply_Message import sendMessagesToComment
from user.models import UserPurchase, User
from contents.models import Content
from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse, CustomPagination
from societies.models import Dynamic
import logging
from django.utils import timezone
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
            queryset = queryset.filter(target_id=target_id,parent_comment_id=0)
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
    pagination_class = CustomPagination
    def get_queryset(self):
        """
        默认只获取动态评论（type='dynamic'）和顶级评论（parent_comment_id=0）
        """
        queryset = super().get_queryset()
        queryset = queryset.filter(type='content')
        # 筛选顶级评论（parent_comment_id为0或None）
        queryset = queryset.filter(parent_comment_id=0)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        获取动态评论列表
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 使用自定义分页响应
            return self.get_paginated_response(serializer.data)
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

    def perform_create(self, serializer):
        # 保存评论并更新Content的comment_count
        user_nickname = self.request.user.user_nickname
        save_kwargs = {
            'user_id': self.request.user.id,
            'type': 'content',
            'user_nickname': user_nickname
        }
        import logging
        if 'parent_comment_id' in self.request.data and self.request.data['parent_comment_id']:
            # 存在该参数时，获取父评论信息并添加回复字段
            parent_comment_id = self.request.data['parent_comment_id']
            obj = Comment.objects.get(id=parent_comment_id)  # 假设传入的ID一定有效（如果需要容错可加try）
            save_kwargs.update({
                'reply_to_user_id': obj.user_id,
                'reply_to_user_nickname': obj.user_nickname
            })
        comment = serializer.save(**save_kwargs)

        # print(f"创建的实例数据: {comment}")
        # print(f"序列化器数据: {serializer.data}")
        # 更新Content表的comment_count
        try:
            content = Content.objects.get(id=comment.target_id)
            content.comment_count = content.comment_count + 1
            content.save(update_fields=['comment_count'])
        except Content.DoesNotExist:
            pass
        except Exception as e:
            logging.exception("更新Content评论数时出错")

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

    # 在CommentViewSet类中添加以下方法

    @extend_schema(
        # 接口描述
        description="通过主评论ID（parent_comment_id）递归获取所有子评论（平级返回），支持分页（每页10条）",
        # 定义参数（会在文档中显示输入框）
        parameters=[
            # parent_id 参数（必填）
            OpenApiParameter(
                name="parent_id",  # 参数名
                location=OpenApiParameter.QUERY,  # 参数位置：查询参数（?parent_id=xxx）
                description="主评论ID（作为parent_comment_id的评论ID）",  # 参数描述
                required=True,  # 是否必填
                type=int,  # 参数类型（整数，匹配评论ID的类型）
            ),
            # 分页页码参数（可选）
            OpenApiParameter(
                name="currentPage",
                location=OpenApiParameter.QUERY,
                description="分页页码（默认第1页）",
                required=False,
                type=int,
                default=1  # 默认值
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='all-children-by-parent')
    def get_all_children_by_parent(self, request,pk=None):
        """
        通过parent_comment_id递归获取所有子评论（平级返回），支持分页
        参数:
        - parent_id: 主评论ID（作为parent_comment_id的评论ID）
        """

        # 获取parent_id参数
        parent_id = request.query_params.get('parent_id')
        # 第几页
        # try:
        #     currentPage = int(request.query_params.get('currentPage', 1))
        #     if currentPage < 1:  # 确保页码不小于1
        #         currentPage = 1
        # except ValueError:
        #     currentPage = 1  # 非法页码默认返回第1页
        if not parent_id:
            return ApiResponse(code=400, message="缺少parent_id参数")
        # 验证主评论是否存在
        try:
            Comment.objects.get(id=parent_id)
        except Comment.DoesNotExist:
            return ApiResponse(code=404, message="当前无评论")

        # 递归获取所有子评论ID（包括所有层级）
        def get_all_child_ids(parent_id):
            """递归获取某个评论下所有子评论的ID"""
            child_ids = []
            # 获取直接子评论
            direct_children = Comment.objects.filter(parent_comment_id=parent_id).values_list('id', flat=True)
            child_ids.extend(direct_children)
            # 递归获取间接子评论
            for child_id in direct_children:
                child_ids.extend(get_all_child_ids(child_id))
            return child_ids

        # 获取所有子评论ID
        all_child_ids = get_all_child_ids(parent_id)
        if not all_child_ids:
            return ApiResponse(data=[], message="没有子评论")
        # 查询所有子评论并按创建时间排序
        queryset = Comment.objects.filter(id__in=all_child_ids).order_by('create_time')

        # 处理分页（默认10条/页，由CustomPagination配置）
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 获取用户上下文数据（包含点赞信息）
            context_data = self.get_user_context_data(request)
            serializer = self.get_serializer(page, many=True, context=context_data)
            return self.get_paginated_response(serializer.data)
        context_data = self.get_user_context_data(request)
        serializer = self.get_serializer(queryset, many=True, context=context_data)
        return ApiResponse(serializer.data)


    @action(detail=True, methods=['post'], url_path='purchase')
    @transaction.atomic
    def perform_video(self, request, pk=None):
        """
       购买视频访问权限
       参数:
       - id: 视频ID
       """
        try:
            # 获取视频对象
            video = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return ApiResponse(code=404, message="视频不存在")
        user = request.user
        if user.gold_coin < video.price:
            return ApiResponse(code=400, message="金币不足,无法购买")
        try:
            user.gold_coin -= video.price
            user.save(update_fields=['gold_coin'])
            userPurchase = UserPurchase.objects.create()
            userPurchase.content_type = "content"
            userPurchase.user = user
            userPurchase.object_id = pk
            userPurchase.purchase_time = datetime.now()
            userPurchase.price = video.price
            userPurchase.save()
        except Exception as e:
            print(repr(e))
            return ApiResponse(code=500, message="购买失败")
        return ApiResponse(message="购买成功", data={'remaining_coins': user.gold_coin})


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
        queryset = queryset.filter(type='dynamic')
        # 筛选顶级评论（parent_comment_id为0或None）
        queryset = queryset.filter(parent_comment_id=0)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        获取动态评论列表
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 使用自定义分页响应
            return self.get_paginated_response(serializer.data)
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

    def perform_create(self, serializer):
        # 保存评论并更新Dynamic的comment_count
        user_nickname = self.request.user.user_nickname
        save_kwargs = {
            'user_id': self.request.user.id,
            'type': 'dynamic',
            'user_nickname': user_nickname
        }
        if 'parent_comment_id' in self.request.data and self.request.data['parent_comment_id']:
            # 存在该参数时，获取父评论信息并添加回复字段
            parent_comment_id = self.request.data['parent_comment_id']
            obj = Comment.objects.get(id=parent_comment_id)  # 假设传入的ID一定有效（如果需要容错可加try）
            save_kwargs.update({
                'reply_to_user_id': obj.user_id,
                'reply_to_user_nickname': obj.user_nickname
            })
        comment = serializer.save(**save_kwargs)
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

    @action(detail=True, methods=['post'], url_path='purchase')
    @transaction.atomic
    def perform_dynamic(self, request, pk=None):
        """
       购买动态访问权限
       参数:
       - id: 动态ID

       """
        try:
            # 获取视频对象
            video = Dynamic.objects.get(pk=pk)
        except Dynamic.DoesNotExist:
            return ApiResponse(code=404, message="动态不存在")
        user = request.user
        if user.gold_coin < video.price:
            return ApiResponse(code=400, message="金币不足,无法购买")
        try:
            user.gold_coin -= video.price
            user.save(update_fields=['gold_coin'])
            userPurchase = UserPurchase.objects.create()
            userPurchase.content_type = "dynamic"
            userPurchase.user = user
            userPurchase.object_id = pk
            userPurchase.purchase_time = datetime.now()
            userPurchase.price = video.price
            userPurchase.save()
        except Exception as e:
            print(repr(e))
            return ApiResponse(code=500, message="购买失败")
        return ApiResponse(message="购买成功", data={'remaining_coins': user.gold_coin})


def example_robot(rot):
    print("执行定时任务")
    print( rot)


def update_vip_status():
    """
    更新用户VIP状态：
    - vip_days为空（NULL）的用户，is_vip设为False
    - vip_days小于当前时间（已过期）的用户，is_vip设为False
    """
    current_time = timezone.now()

    # 1. 筛选 vip_days 为空且当前是VIP的用户
    null_vip_users = User.objects.filter(vip_days__isnull=True, is_vip=True)
    # 2. 筛选 vip_days 过期且当前是VIP的用户
    expired_vip_users = User.objects.filter(vip_days__lt=current_time, is_vip=True)
    # 合并两个查询集（使用 | 操作符，无需Q函数）
    target_users = null_vip_users | expired_vip_users
    # 批量更新状态
    updated_count = target_users.update(is_vip=False)
    return f"已更新 {updated_count} 位用户的VIP状态为False（包含未设置VIP和已过期用户）"


@extend_schema(tags=['任务执行 定时'])
class TaskSchedulerView(APIView):
    """配置定时任务的接口"""
    @extend_schema(
        summary='创建机器人任务',
        description='根据robot_id创建机器人评论任务',
        parameters=[
            OpenApiParameter(
                name='robot_id',
                location=OpenApiParameter.QUERY,
                description='机器人ID',
                required=True,
                type=int
            ),
            OpenApiParameter(
                name='method',
                location=OpenApiParameter.QUERY,
                description='区分执行，comment、reply、timing',
                required=True,
                type=str
            )
        ],
        request=None,
        responses={
            200: {
                'description': '任务创建成功',
            },
            400: {
                'description': '参数错误或任务创建失败',
            }
        }
    )
    def post(self, request):
        """
        创建机器人任务
        参数:
        - robot_id: 机器人ID（路径参数）
        """
        try:
            method = request.query_params.get('method')
            robot_id = request.query_params.get('robot_id')
            if not method:
                return ApiResponse(code=400, message='method参数是必需的')
            if not robot_id:
                return ApiResponse(code=400, message='robot_id是必需的')
            # 获取评论对象以获取exec_id
            try:
                if method == 'comment':
                    job_id = f'mission_comment_{robot_id}'
                    scheduler.add_job(
                        func=sendMessagesToComment,
                        trigger='daily',  # 明确指定具体小时
                        job_id=job_id,
                        nums=5,
                        args=(robot_id, method,),
                        kwargs={}
                    )
                    logging.info('添加评论任务成功')
                elif method == 'reply':
                    job_id = f'mission_reply_{robot_id}'
                    scheduler.add_job(
                        func=sendMessagesToComment,
                        trigger='daily',  # 明确指定具体小时
                        job_id=job_id,
                        nums=5,
                        args=(robot_id, method,),
                        kwargs={}
                    )
                    logging.info('回复评论任务成功')
                elif method == 'timing':
                    job_id = f'update_vip_status{robot_id}'
                    scheduler.add_job(
                        update_vip_status,
                        trigger='timing',
                        job_id=job_id,
                        args='',
                        kwargs={}
                    )
                    logging.info('添加定时任务成功')
                else:
                    return ApiResponse(code=400, message='method参数错误')
                # 添加机器人评论任务
            except Comment.DoesNotExist:
                return ApiResponse(code=404, message='未找到对应的评论任务')
            return ApiResponse(message='任务创建成功')
        except Exception as e:
            return ApiResponse(code=400, message=f"操作失败：{str(e)}")

# 在后续使用 针对任务的暂停 恢复 删除
@extend_schema(tags=['任务执行 定时'])
class TaskSchedulerViewAction(APIView):
    """配置定时任务的接口"""
    @extend_schema(
        summary='任务的暂停、恢复、删除、获取',
        description='对指定任务执行暂停、恢复、删除、获取等操作',
        parameters=[
            OpenApiParameter(
                name='robot_id',
                location=OpenApiParameter.QUERY,
                description='机器人ID',
                required=True,
                type=int
            ),
            OpenApiParameter(
                name='method',
                location=OpenApiParameter.QUERY,
                description='区分执行 comment、reply、timing',
                required=True,
                type=str
            ),
            OpenApiParameter(
                name='action',
                location=OpenApiParameter.QUERY,
                description='pause，resume、get、delete',
                required=True,
                type=str
            )
        ],
        responses={
            200: {
                'description': '操作成功',
            },
        }
    )
    def post(self, request):
        try:
            method = request.query_params.get('method')
            robot_id = request.query_params.get('robot_id')
            action = request.query_params.get('action')
            job_id = f'mission_{method}_{robot_id}'
            if not robot_id or not method:
                return ApiResponse(code=400, message='定时任务ID和操作方法是必需的')
            method_map = {
                'pause': self.pause_job,
                'resume': self.resume_job,
                'get': self.get_job,
                'delete': self.delete_job
            }
            if action == 'pause':
                # 暂停任务：更新状态为 paused
                print("暂停")
            response = method_map[action](job_id)
            return response
        except Exception as e:
            return ApiResponse(code=400, message=f"操作失败：{str(e)}")
    def pause_job(self, job_id):
        scheduler.pause_job(job_id)
        return ApiResponse(message=f'任务已暂停')
    def resume_job(self, job_id):
        scheduler.resume_job(job_id)
        return ApiResponse(message=f'任务已继续')
    def get_job(self, job_id):
        scheduler.get(job_id)
    def delete_job(self, job_id):
        scheduler.delete_job(job_id)
        return ApiResponse(message=f'任务已删除')
