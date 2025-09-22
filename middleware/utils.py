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
