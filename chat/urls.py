from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chat.views import MessageViewSet, SessionViewSet, SettingsViewSet

router = DefaultRouter()
router.register(r'message', MessageViewSet)
router.register(r'session', SessionViewSet)
router.register(r'setting', SettingsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]