from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
# Create your views here.

# 序列化器定义 API 表示。
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

# ViewSets 定义视图行为。
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
