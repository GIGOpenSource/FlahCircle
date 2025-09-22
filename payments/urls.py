from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.views import PaymentViewSet, PaymentSettingsViewSet

router = DefaultRouter()
router.register(r'pay', PaymentViewSet)
router.register(r'settings', PaymentSettingsViewSet)

urlpatterns = [
    path('', include(router.urls)),

]