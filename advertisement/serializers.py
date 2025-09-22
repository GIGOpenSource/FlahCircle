# user/serializers.py
from rest_framework import serializers
from advertisement.models import Advertisement


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = [
            'id', 'name', 'title', 'description', 'type',
            'image_url', 'click_url', 'alt_text', 'target_type',
            'is_active', 'sort_order', 'create_time', 'update_time'
        ]
        read_only_fields = ['id', 'create_time', 'update_time']  # 只读字段