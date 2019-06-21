import django_filters
from django.shortcuts import render
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import Http404
from django.http import HttpResponse
from django.contrib.auth import *
from django.contrib.auth.models import User, Group
from django_filters.rest_framework import DjangoFilterBackend
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import *
from .serializers import *

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.dispatch import receiver
from django.db.models.signals import post_save
import json

# Create your views here.
from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='Pastebin API')

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


#  用户注册
@csrf_exempt 
def user_signup(request):
    
    if request.method == 'POST':
        
        req = json.loads(request.body)
        # logic to check username/password
        # username = request.POST.get('email')
        # password = request.POST.get('password')   
         # logic to check username/password
        # username = request.POST['username']
        # password = request.POST['password']
        # email = request.POST['email']
        # phone = request.POST['phone']
        # avatar = request.FILES['avatar']
        first_name = req.get('name')
        stuId = req.get('stuId')
        birth = req.get('birth')
        sex = req.get('sex')
        grade = req.get('grade')
        major = req.get('major')
        email = req.get('email')
        password = req.get('password')

        try:
            new_user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name
            )
        except:
            response_data = {
                "code" : 500,
                "msg" : "用户已存在"
            }
            return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)

        new_user.set_password(password)
        new_user.save()

        profile = Profile.objects.create(
            user=new_user,
            balance=0,
            stuId=stuId,
            birth=birth,
            sex=sex,
            grade=grade,
            major=major
        )
        profile.save()

        response_data = {
            "code" : 200,
            "msg" : "注册用户成功"
        }
        return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)

    # if request.method == 'GET':
        

#  用户登录
@csrf_exempt 
def user_login(request):
    
    if request.method == 'POST':
        # If we didn't post, send the test cookie along with the login form.
        request.session.set_test_cookie()

        # Check that the test cookie worked (we set it below):
        if request.session.test_cookie_worked():

            # The test cookie worked, so delete it.
            request.session.delete_test_cookie()
            req = json.loads(request.body)
            # logic to check username/password
            # username = request.POST.get('email')
            # password = request.POST.get('password')   
            email = req.get('email')
            password = req.get('password')

            user = authenticate(username=email, password=password)  #用户验证
            if user:
                login(request, user)  #用户登录
                request.session['user_id'] = user.id
                # user_serialized = UserSerializer(user)
                profile_serialized = ProfileSerializer(Profile.objects.get(user=user))
                response_data = {
                    "code" : 200,
                    "msg" : "登录成功",
                    # "user" : user_serialized.data,
                    "profile" : profile_serialized.data
                }
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            else:
                response_data = {
                    "code" : 500,
                    "msg" : "用户名（邮箱名）或密码不正确",
                    "profile" : None
                }
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
        
        # The test cookie failed, so display an error message. If this
        # were a real site, we'd want to display a friendlier message.
        else:
            return HttpResponse("Please enable cookies and try again.")
    
    return HttpResponse("Method is not POST.", status=status.HTTP_405_METHOD_NOT_ALLOWED)


#  用户登出
@csrf_exempt 
def user_logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return HttpResponse("You're logged out.")


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

    def create(self, request):
        if request.method == 'POST':
            user = request.user
            available_balance = Profile.objects.get(user=user).available_balance
            title = request.POST['title']
            description = request.POST['description']
            poll = request.FILES['poll']
            fee = int(request.POST['fee'])
            participant_quota = int(request.POST['participant_quota'])
            due_date = request.POST['due_date']

            if available_balance < fee * participant_quota:
                return HttpResponse("Not enough balance.")

            task = Task.objects.create(
                issuer=user,
                title=title,
                description=description,
                poll=poll,
                fee=fee,
                participant_quota=participant_quota,
                due_date=due_date
            )
            task.save()
            return HttpResponse("Create a new task.")
            

    # def update(self, request, pk=None):
    # 

    # def retrieve(self, request, pk=None):
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
    
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        if request.method == 'POST':
            user = request.user
            task_id = request.POST['task_id']
            task = Task.objects.get(pk=task_id)
            task_status = task.status

            if task_status == 'INVALID':
                return HttpResponse("TASK INVALID")
            elif task_status == 'CANCELLED':
                return HttpResponse("TASK CANCELLED")
            elif task_status == 'CLOSED':
                return HttpResponse("TASK CLOSED")
            elif task_status == 'QUOTA FULL':
                return HttpResponse("TASK QUOTA FULL")
            
            description = task.description
            poll = request.FILES['poll']
            rate = int(request.POST['rate'])
            comment = request.POST['comment']

            participantship = Participantship.objects.create(
                user=user,
                task=task,
                description=description,
                poll=poll,
                rate=rate,
                comment=comment
            )
            participantship.save()
            return HttpResponse("Create a new participantship.")



class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

# def UserLogin():
