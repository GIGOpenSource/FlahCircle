from django.utils import timezone
from datetime import timedelta
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    自定义Token认证类，支持token过期机制
    """
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed({
                'code': 401,
                'message': '无效的Token',
                'data': {}
            })
        if not token.user.is_active:
            raise AuthenticationFailed({
                'code': 401,
                'message': '用户账户已被禁用',
                'data': {}
            })
        # 检查token是否过期（4小时）
        if timezone.now() > token.created + timedelta(hours=4):
            raise AuthenticationFailed({
                'code': 401,
                'message': 'Token已过期，请重新登录',
                'data': {}
            })
        return (token.user, token)