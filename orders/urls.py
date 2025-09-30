from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.views import OrderViewSet  # 导入回调视图

router = DefaultRouter()
router.register(r'', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # 将回调视图路径添加到urlpatterns
]