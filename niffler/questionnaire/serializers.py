from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
# 序列化器定义 API 表示。

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # Tuple of serialized model fields (see link [2])
        fields = '__all__'
        # fields = ( "id", "username", "password", "email")


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('user', 'phone', 'balance', 'avatar', 'birth', 
                  'stuId', 'grade', 'major', 'sex', 'available_balance',)
        read_only_fields = ('balance', )


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'tag_set', 'poll', 'issuer', 
                  'fee', 'participant_quota', 'created_date', 'due_date', 
                  'participants', 'claimers', 'cancelled', 
                  'valid_participant_amount', 'remaining_quota', 'status')
        read_only_fields = ('issuer', 'claimers', 'cancelled')

class ParticipantshipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Participantship
        fields = '__all__'

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'