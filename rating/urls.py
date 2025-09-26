from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.views import PaymentViewSet, PaymentSettingsViewSet
from rating.views import RatingViewSet

router = DefaultRouter()
router.register(r'', RatingViewSet)

urlpatterns = [
    path('', include(router.urls)),

]