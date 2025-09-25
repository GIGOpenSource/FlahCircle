from rest_framework import serializers
from tasks.models import Reward, Template


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'
        read_only_fields = ('create_time', 'update_time')


class TaskRewardSerializer(serializers.ModelSerializer):
    task_template_id = serializers.IntegerField(source='task_template.id', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    task_template_name = serializers.CharField(source='task_template.name', read_only=True)
    task_template_description = serializers.CharField(source='task_template.description', read_only=True)
    task_template_type = serializers.CharField(source='task_template.type', read_only=True)
    task_template_amount = serializers.IntegerField(source='task_template.amount', read_only=True)
    task_template_image_url = serializers.CharField(source='task_template.image_url', read_only=True)
    task_template_category = serializers.CharField(source='task_template.category', read_only=True)
    task_template_is_active = serializers.BooleanField(source='task_template.is_active', read_only=True)
    
    class Meta:
        model = Reward
        fields = '__all__'
        read_only_fields = ('create_time', 'update_time', 'claimed_time', 'completed_time')
