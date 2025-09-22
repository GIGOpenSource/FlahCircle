# user/views.py
from rest_framework import status, generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer, UserLoginSerializer
from middleware.utils import ApiResponse

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return ApiResponse(data={
                'user_id': user.id,
                'username': user.username,
                'token': token.key
            })
        return ApiResponse(code=400, message=serializer.errors)

class CustomLoginView(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    token, _ = Token.objects.get_or_create(user=user)
                    return ApiResponse(data={
                        'user_id': user.id,
                        'username': user.username,
                        'token': token.key,
                        'member_level': user.member_level  # 返回会员等级
                    })
                return ApiResponse(code=401, message='密码错误')
            except User.DoesNotExist:
                return ApiResponse(code=401, message='用户不存在')
        return ApiResponse(code=400, message=serializer.errors)