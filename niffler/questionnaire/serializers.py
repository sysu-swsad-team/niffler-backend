from django.contrib.auth.models import User#, Group
from rest_framework import serializers
from .models import *
# 序列化器定义 API 表示。

# class EmailVerifySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EmailVerify
#         # Tuple of serialized model fields (see link [2])
#         fields = '__all__'
#         # fields = ( "id", "username", "password", "email")

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # Tuple of serialized model fields (see link [2])
        fields = '__all__'
        # fields = ( "id", "username", "password", "email")


# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Group
#         fields = ('url', 'name')

class ProfileSerializer(serializers.ModelSerializer):
        

    first_name = serializers.SerializerMethodField()
    def get_first_name(self, obj):
        return obj.user.first_name
    
    issued_tasks = serializers.SerializerMethodField()
    def get_issued_tasks(self, obj):
        return list(obj.user.issued_tasks.values_list('id', flat=True))
    
    participanted_tasks = serializers.SerializerMethodField()
    def get_participanted_tasks(self, obj):
        return list(obj.user.participanted_tasks.values_list('id', flat=True))
    
    participantship_set = serializers.SerializerMethodField()
    def get_participantship_set(self, obj):
        return list(obj.user.participantship_set.values_list('id', flat=True))
    
    tag_set = serializers.SerializerMethodField()
    def get_tag_set(self, obj):
        return list(obj.user.tag_set.values_list('id', flat=True))

    class Meta:
        model = Profile
        fields = ('user', 'phone', 'balance', 'avatar', 'birth', 
                  'stuId', 'grade', 'major', 'sex', 'available_balance',
                  'first_name', 'issued_tasks', 'participanted_tasks', 
                  'participantship_set', 'tag_set')
        read_only_fields = ('balance', )


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'tag_set', 'poll', 'issuer', 
                  'fee', 'participant_quota', 'created_date', 'due_date', 
                  'participants', 'claimers', 'cancelled', 'task_type',
                  'valid_participant_amount', 'remaining_quota', 'status',
                  'issuer_first_name', 'participantship_set')
        read_only_fields = ('issuer', 'claimers', 'cancelled')

# class ParticipantshipSerializer(serializers.HyperlinkedModelSerializer):
class ParticipantshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participantship
        fields = '__all__'

# class TagSerializer(serializers.HyperlinkedModelSerializer):
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
