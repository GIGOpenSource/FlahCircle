# user/serializers.py
from rest_framework import serializers
from tasks.models import Reward, Template


class TaskRewardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reward
        fields = '__all__'


class TaskTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Template
        fields = '__all__'