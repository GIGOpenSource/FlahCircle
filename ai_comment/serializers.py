from rest_framework import serializers
from .models import AIConfig

class AIConfigSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(help_text='密钥明文返回')
    class Meta:
        model = AIConfig
        fields = [
            'id', 'name', 'provider', 'model', 'enabled', 'is_default', 'priority',
            'api_key', 'base_url', 'region', 'api_version', 'organization_id',
            'created_at', 'updated_at', 'created_by'
        ]
        read_onlu_fields=['created_at', 'updated_at', 'created_by']

    def validate(self, attrs):
        provider = attrs.get('provider', getattr(self.instance, 'provider', None))
        base_url = attrs.get('base_url', getattr(self.instance, 'base_url', ''))
        api_version = attrs.get('api_version', getattr(self.instance, 'api_version', ''))
        region = attrs.get('region', getattr(self.instance, 'region', ''))
        model = attrs.get('model', getattr(self.instance, 'model', ''))
        api_key = attrs.get('api_key', getattr(self.instance, 'api_key', ''))
        if not model:
            raise serializers.ValidationError('model 必填')
        if provider in {'openai', 'deepseek'}:
            if not api_key:
                raise serializers.ValidationError('api_key 必填（openai/deepseek）')
            # 默认 base_url
            if provider == 'deepseek' and not base_url:
                attrs['base_url'] = 'https://api.deepseek.com'

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 若未传 api_key，不覆盖原值
        if 'api_key' not in validated_data:
            validated_data['api_key'] = instance.api_key
        return super().update(instance, validated_data)