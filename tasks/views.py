from rest_framework import viewsets
from tasks.models import Reward, Template
from tasks.serializers import TaskRewardSerializer, TaskTemplateSerializer


class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = TaskRewardSerializer


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TaskTemplateSerializer