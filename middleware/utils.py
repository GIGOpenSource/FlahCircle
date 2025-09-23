from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


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
    page_size = 10  # 默认每页条数
    page_query_param = 'currentPage'  # 关键：匹配前端的 "currentPage" 参数（指定页码）
    page_size_query_param = 'pageSize'  # 匹配前端的 "pageSize" 参数（指定每页条数）
    max_page_size = 100  # 最大每页条数限制

    def get_paginated_response(self, data):
        print("分页查询")
        # 现在这个方法会在分页生效时被自动调用
        return ApiResponse({
            'pagination': {
                'page': self.page.number,  # 当前页码
                'page_size': self.page_size,  # 每页条数
                'total': self.page.paginator.count,  # 总记录数
                'total_pages': self.page.paginator.num_pages  # 总页数
            },
            'results': data
        })