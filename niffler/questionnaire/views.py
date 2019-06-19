import django_filters
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from .models import *
from .serializers import *

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404

# Create your views here.

class UserFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = User
        fields = ['username']

# ViewSets 定义视图行为。
class UserViewSet(viewsets.ModelViewSet):
    """
    允许用户查看或编辑的 API 端点。
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = UserFilter


class GroupViewSet(viewsets.ModelViewSet):
    """
    允许组查看或编辑的 API 端点。
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class TaskViewSet(viewsets.ModelViewSet):
    """
    允许 Task 查看或编辑的 API 端点。
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    
    queryset = Task.objects.all()
    serializer_class = TaskSerializer     

    # def create(self, request):


    # def retrieve(self, request, pk=None):
    # pass

    # def update(self, request, pk=None):
    # pass

    # def partial_update(self, request, pk=None):
    # pass

    # def destroy(self, request, pk=None):
    # pass

    # """
    # 如果你有特别的需要被路由到的方法,可以将它们标记为需要路由使用@detail_route或@list_route修饰符。
    # """

    # @detail_route(methods=[‘post’], permission_classes=[IsAdminOrIsSelf])
    # def set_password(self, request, pk=None):

    # """
    # 可以通过访问^users/{pk}/set_password/$来访问改视图


class ParticipantshipViewSet(viewsets.ModelViewSet):
    queryset = Participantship.objects.all()
    serializer_class = ParticipantshipSerializer
 
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer