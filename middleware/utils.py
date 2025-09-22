from rest_framework.response import Response

class ApiResponse(Response):
    """统一响应格式"""
    def __init__(self, data=None, message='success', code=200, **kwargs):
        response_data = {
            'code': code,       # 状态码（200成功）
            'message': message, # 提示信息
            'data': data        # 数据（错误时为None）
        }
        super().__init__(response_data, status=200,** kwargs)  # HTTP状态码固定200，业务码用code字段区分