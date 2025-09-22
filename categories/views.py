from rest_framework import viewsets
from categories.models import Category
from categories.serializers import CategorySerializer
from middleware.base_views import BaseViewSet


class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
