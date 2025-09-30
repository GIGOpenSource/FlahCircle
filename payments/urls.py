from django.urls import path, include
from rest_framework.routers import DefaultRouter


from payments.views import PaymentViewSet, PaymentSettingsViewSet, BenefitsViewSet

router = DefaultRouter()
router.register(r'pay', PaymentViewSet)
router.register(r'settings', PaymentSettingsViewSet)
router.register(r'benefits', BenefitsViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
