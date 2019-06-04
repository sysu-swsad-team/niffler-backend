from django.contrib.auth.models import User, Group
from rest_framework import serializers

# 序列化器定义 API 表示。
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        # field = '__all__'
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')