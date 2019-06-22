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
from rest_framework.decorators import action

from .models import *
from .serializers import *

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.dispatch import receiver
from django.db.models.signals import post_save
import json

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
                    "email" : user.email,
                    "name" : user.first_name,
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
        request.session.flush()
        logout(request)
    except KeyError:
        pass
    return HttpResponse("You're logged out.")

# 更改个人头像
@csrf_exempt 
def user_avatar(request):
    response_data = {}
    if request.method == 'POST':
        # req = json.loads(request.body)
        # avatar = req.get('avatar')
        # avatar = request.body
        if request.user.is_authenticated:  
            avatar = request.FILES['file']
            print(avatar)
            # try:
            #     with open('avatar/' + request.user.email + '.jpeg', 'wb+') as destination:
            #         destination.write(avatar)
            # except:
            #     response_data = {
            #         "code" : 500,
            #         "msg" : "请求错误"
            #     }
            #     return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)

            # return HttpResponse(avatar, content_type="image/jpeg", status=status.HTTP_200_OK)
        
            if avatar:
                user_id = request.session['user_id']
                profile = Profile.objects.get(user=request.user)
                profile.avatar = avatar
                profile.save()

                response_data["code"] = 200
                response_data["msg"] = "头像更新成功"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            else:
                response_data["code"] = 500
                response_data["msg"] = "请求错误"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
        else:
            response_data["code"] = 500
            response_data["msg"] = "用户未登录"
            return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
    # if request.method == 'GET':
    #     user_id = request.session['user_id']
    #     user=User.objects.get(pk=user_id)
    #     profile = Profile.objects.get(user=user)
    #     avatar = profile.avatar
    #     try:
    #         with open(avatar, "rb") as f:
    #             return HttpResponse(f.read(), content_type="image/jpeg", status=status.HTTP_200_OK)
    #     except IOError:
    #         red = Image.new('RGBA', (1, 1), (255,0,0,0))
    #         response = HttpResponse(content_type="image/jpeg", status=status.HTTP_200_OK)
    #         red.save(response, "JPEG")
    #         return response

        # user_id = request.session['user_id']
        # profile = Profile.objects.get(user=User.objects.get(pk=user_id))

        # response_data = {
        #     "code" : 200,
        #     "msg" : "获得头像 url 成功",
        #     "avatar" : profile.avatar
        # }

        # return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)


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

    @action(detail=False, methods=['get'])
    @csrf_exempt
    def get_queryset(self):
        queryset = Task.objects.all().order_by('created_date')

        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.filter(title=title)

        issuer_name = self.request.query_params.get('sponsor', None)
        if issuer_name is not None:
            user = get_object_or_404(User, first_name=issuer_name)
            queryset = queryset.filter(issuer=user)

        filtered = [x for x in queryset if x.status=='UNDERWAY' and x.task_type=='问卷']

        return filtered

    def create(self, request, *args, **kwargs):
        """
        发布问卷
        """
        user = request.user
        form = request.data
        available_balance = user.profile.available_balance
        title = form['title']
        description = form['description']
        poll = form['question']
        try:
            fee = int(form['fee']) if form['fee'] else None
            participant_quota = int(form['maxNumber']) \
                           if form['maxNumber'] else None
        except:
            response_data = {
                "code" : status.HTTP_400_BAD_REQUEST,
                "msg" : "金额与参与名额必须为数字"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_400_BAD_REQUEST)
        due_date = form['dueDate'] # maybe also need check
        task_type = form['taskType'] # maybe also need check
        tag_set = form['tagSet'] # maybe also need check
        try:
            assert(tag_set == None or isinstance(tag_set, list))
        except:
            response_data = {
                "code" : status.HTTP_400_BAD_REQUEST,
                "msg" : "标签必须为空或数组"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_400_BAD_REQUEST)

        if fee:
            if not participant_quota:
                response_data = {
                    "code" : status.HTTP_400_BAD_REQUEST,
                    "msg" : "设定金额时必须同时设定参与名额"
                }
                return HttpResponse(json.dumps(response_data), 
                                        status=status.HTTP_400_BAD_REQUEST)
            if available_balance < fee * participant_quota:
                response_data = {
                    "code" : status.HTTP_400_BAD_REQUEST,
                    "msg" : "可用余额不足"
                }
                return HttpResponse(json.dumps(response_data), 
                                        status=status.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.create(
                issuer=user,
                title=title,
                description=description,
                poll=poll,
                fee=fee,
                participant_quota=participant_quota,
                due_date=due_date,
                task_type=task_type
            )
            task.save()

            if tag_set:
                for tag_name in tag_set:
                    if Tag.objects.filter(name=tag_name).exists():
                        tag_obj = Tag.objects.get(name=tag_name)
                    else:
                        tag_obj = Tag.objects.create(name=tag_name)
                    tag_obj.tasks.add(task)
        except:
            response_data = {
                "code" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                "msg" : "发布失败"
            }
            return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            "code" : status.HTTP_201_CREATED,
            "msg" : "发布成功"
        }
        return HttpResponse(json.dumps(response_data), 
                                status=status.HTTP_201_CREATED)

    # def update(self, request, pk=None):
    # 
    def retrieve(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        task_serialized = TaskSerializer(task)
        return HttpResponse(json.dumps(task_serialized.data), status=status.HTTP_200_OK)

    # def partial_update(self, request, pk=None):
    # pass
    def destroy(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return HttpResponse(status=status.HTTP_200_OK)
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
        response_data = {}
        if request.method == 'POST':
            user = request.user
            form = json.loads(request.body)

            task_id = form['task_id']
            task = Task.objects.get(pk=task_id)
            task_status = task.status

            if task_status == 'INVALID':
                response_data['code'] = 500
                response_data['msg'] = "问卷存在争议"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            elif task_status == 'CANCELLED':
                response_data['code'] = 500
                response_data['msg'] = "问卷被发布者取消"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            elif task_status == 'CLOSED':
                response_data['code'] = 500
                response_data['msg'] = "问卷已经过截至日期"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            elif task_status == 'QUOTA FULL':
                response_data['code'] = 500
                response_data['msg'] = "问卷参与人数已满"
                return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
            
            description = task.description
            poll = form['poll']
            rate = int(form['rate'])
            comment = form['comment']

            participantship = Participantship.objects.create(
                user=user,
                task=task,
                description=description,
                poll=poll,
                rate=rate,
                comment=comment
            )
            participantship.save()

            response_data['code'] = 200
            response_data['msg'] = "参与问卷成功"
            return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

# def UserLogin():
