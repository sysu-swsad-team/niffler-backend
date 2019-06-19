from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *

# 序列化器定义 API 表示。
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_on_fields = ('balance')

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_on_fields = ('issuer', 'claimers', 'cancelled')

class ParticipantshipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Participantship
        fields = '__all__'

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'