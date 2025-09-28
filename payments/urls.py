from django.urls import path, include
from rest_framework.routers import DefaultRouter

from orders.views import OrderPaymentCallbackView
from payments.views import PaymentViewSet, PaymentSettingsViewSet, PaymentCallbackView, BenefitsViewSet

router = DefaultRouter()
router.register(r'pay', PaymentViewSet)
router.register(r'settings', PaymentSettingsViewSet)
router.register(r'benefits', BenefitsViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('callback/', PaymentCallbackView.as_view(), name='payment_callback'),
    path('payment-callback/', OrderPaymentCallbackView.as_view(), name='order-payment-callback'),

]
