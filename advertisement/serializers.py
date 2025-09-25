# user/serializers.py
from rest_framework import serializers
from advertisement.models import Advertisement
from rest_framework.pagination import PageNumberPagination

from middleware.base_views import BaseViewSet
from middleware.utils import ApiResponse


def validate_type(value):
    """验证 type 字段"""
    if not value or value.strip() == '':
        raise serializers.ValidationError("广告类型(type)字段不能为空")
    return value.strip()


class AdvertisementSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=True, allow_blank=False, max_length=255)

    class Meta:
        model = Advertisement
        fields = [
            'id', 'name', 'title', 'description', 'type',
            'image_url', 'click_url', 'alt_text', 'target_type',
            'is_active', 'sort_order', 'is_vip','price','create_time', 'update_time'
        ]
        read_only_fields = ['id', 'create_time', 'update_time']  # 只读字段



