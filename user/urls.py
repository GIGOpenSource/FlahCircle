from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, CustomLoginView, UserViewSet, GroupViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)  # 用户管理CRUD路由
router.register(r'groups', GroupViewSet)  # 用户组管理CRUD路由

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', CustomLoginView.as_view(), name='user-login'),
    path('', include(router.urls)),
]