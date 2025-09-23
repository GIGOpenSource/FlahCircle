# user/serializers.py
from rest_framework import serializers
from tasks.models import Reward, Template


class TaskRewardSerializer(serializers.ModelSerializer):
    task_template_id =serializers.CharField()
    # description =serializers.CharField(source='task.description')
    print(task_template_id)
    class Meta:
        model = Reward
        fields = '__all__'


class TaskTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Template
        fields = '__all__'
