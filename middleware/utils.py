from django.core.paginator import EmptyPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import exception_handler


class ApiResponse(Response):
    """统一响应格式（修复后）"""
    def __init__(self, data=None, message='success', code=200, **kwargs):
        # 确保message是字符串类型
        if not isinstance(message, str):
            # 如果是字典类型（如表单验证错误），转换为字符串
            if isinstance(message, dict):
                # 将字典转换为用分号分隔的键值对字符串
                message = "; ".join([f"{k}: {', '.join(v)}" for k, v in message.items()])
            else:
                # 其他类型强制转换为字符串
                message = str(message)
        # 确保data不为null，如果为null则设为空字典
        if data is None:
            data = {}

        response_data = {
            'code': code,
            'message': message,
            'data': data
        }
        # 始终使用200作为HTTP状态码
        super().__init__(response_data, status=200, **kwargs)



class CustomPagination(PageNumberPagination):
    page_size = 20  # 默认每页条数
    page_query_param = 'currentPage'  # 关键：匹配前端的 "currentPage" 参数（指定页码）
    page_size_query_param = 'pageSize'  # 匹配前端的 "pageSize" 参数（指定每页条数）
    max_page_size = 999  # 最大每页条数限制

    def get_paginated_response(self, data):
        print("分页查询")
        # 现在这个方法会在分页生效时被自动调用
        return ApiResponse({
            'pagination': {
                'page': self.page.number,  # 当前页码
                'page_size': self.page.paginator.per_page,  # 使用实际的page_size参数
                'total': self.page.paginator.count,  # 总记录数
                'total_pages': self.page.paginator.num_pages  # 总页数
            },
            'results': data
        })

    def paginate_queryset(self, queryset, request, view=None):
        """
        处理超出范围的页码请求
        """
        try:
            return super().paginate_queryset(queryset, request, view=view)
        except Exception as e:
            # 捕获所有分页相关的异常
            if "Invalid page" in str(e) or isinstance(e, EmptyPage):
                # 当请求的页码无效时，返回空结果而不是抛出异常
                self.request = request
                # 创建一个空的分页结果
                page_size = self.get_page_size(request) or self.page_size
                from django.core.paginator import Paginator
                empty_paginator = Paginator([], page_size)
                self.page = empty_paginator.page(1)
                return []
            # 如果是其他异常，重新抛出
            raise e

def custom_exception_handler(exc, context):
    """
    自定义异常处理函数
    """
    # 调用默认的异常处理函数
    response = exception_handler(exc, context)

    # 如果是页面无效的错误，返回自定义响应
    if isinstance(exc, NotFound) and ("Invalid page" in str(exc.detail) or "无效页面" in str(exc.detail)):
        return ApiResponse(
            data={
                'pagination': {
                    'page': 1,
                    'page_size': 20,
                    'total': 0,
                    'total_pages': 0
                },
                'results': []
            },
            message="请求的页面超出范围，返回空结果",
            code=200
        )

    # 对于其他异常，返回默认处理结果
    return response